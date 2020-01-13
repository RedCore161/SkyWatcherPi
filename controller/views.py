import datetime
import ntpath
import os
import time

import cv2
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic.list import ListView

import SkyWatcherCC.cameraController as cc
from SkyWatcherCC.settings import FULL_CAPUTRING_PATH, MOCK_CAMERA, THUMBNAIL_PATH, MOCK_PATH_A, MOCK_PATH_B
from SkyWatcherCC.views import HttpSuccess, HttpFailed
from controller.forms import CaptureConfigForm, CaptureFlow
from controller.models import ConfigMapping, ImageFile, CaptureConfig
from controller.helper import start_as_thread
from threading import Thread


def start_new_thread(func):
    """
    wrapper-decorator to start a thread
    :param func: function that will be started as a thread
    :return: /
    """
    def decorator(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator

# -----------------------------------------------------------------------------------
# ---- I M A G E - C A P T U R I N G ------------------------------------------------
# -----------------------------------------------------------------------------------


def capture(request, config_id=None):
    """
    Test with: curl -X POST http://127.0.0.1:8080/api/capture
    :param config_id: if given, reads the parameters from the given CaptureConfig, otherwise from the request
    :param request: needs iso, aperture, exposure and image_format
    :return: statuscode 200 or 400 (for ajax)
    """

    config = None

    filename = '{0:%Y-%m-%d_%H-%M-%S}.jpg'.format(datetime.datetime.now())
    path = '{0}{1:%Y-%m-%d}/'.format(FULL_CAPUTRING_PATH, datetime.datetime.now())

    if config_id:
        config = CaptureConfig.objects.get(pk=config_id)
        iso = config.iso
        aperture = config.aperture
        exposure = config.exposure
        bulb_time = config.bulb_time
        image_format = config.image_format

    else:
        iso = request.POST.get("iso")
        aperture = request.POST.get("aperture")
        exposure = request.POST.get("exposure")
        bulb_time = request.POST.get("bulb_time")
        image_format = request.POST.get("image_format")

    if cc.is_camera_present():
        print("Capturing START!", time.time(), bulb_time, config_id)
        if cc.capture_image(path, filename, iso, aperture, exposure, image_format, bulb_time) == 0:
            print("Capturing DONE!", time.time())
            result = {'filepath': path + filename}

            save_image(config, filename, path, image_format, result['filepath'][1:])

            return HttpSuccess(result)

    elif MOCK_CAMERA:
        if bulb_time > 0:
            time.sleep(bulb_time)
        else:
            time.sleep(float(exposure))

        filename = "mock_image.png"
        result = {'filepath': MOCK_PATH_A + filename}

        save_image(config, filename, MOCK_PATH_B, image_format, result['filepath'][1:])

        return HttpSuccess(result)

    return HttpFailed()


# -----------------------------------------------------------------------------------
# ---- V I E W - C L A S S E S ------------------------------------------------------
# -----------------------------------------------------------------------------------

class CaptureConfigDetail(DetailView):
    """
    DetailView of a given CaptureConfig
    """
    model = CaptureConfig

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mapping = ConfigMapping.objects.get(flow_id=self.request.GET.get('flow_id'), config_id=context['object'])
        context['repeats'] = mapping.repeats
        return context


class ConfigGalleryView(ListView):
    """
    ListView for all images of a given CaptureConfig
    """
    model = ImageFile
    context_object_name = 'images'
    template_name = 'dummies/dummy_gallery.html'
    object_list = None
    queryset = None

    def get_queryset(self):
        return ImageFile.objects.filter(config_id=self.kwargs['pk'])


class ConfigMappingListView(ListView):
    """
    ListView for all connected and unconnected CaptureConfigs of a given CaptureFlow
    """
    model = ConfigMapping
    simple_view = False
    object_list = None
    queryset = None

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_queryset(self):
        return ConfigMapping.objects.filter(flow__id=self.kwargs['pk']).order_by('order')

    def get_context_data(self, **kwargs):
        context = super(ConfigMappingListView, self).get_context_data(**kwargs)
        context['flow_id'] = self.kwargs['pk']
        context['object_list'] = self.get_queryset()

        if not self.simple_view:
            ids = []
            for mapping in context['object_list']:
                ids.append(mapping.config_id)
            others = CaptureConfig.objects.exclude(pk__in=ids)

            context['other_configs'] = others

        return context


class CaptureFlowListView(ListView):
    """
    ListView for CaptureFlows
    """
    model = CaptureFlow
    context_object_name = 'list_flows'
    queryset = CaptureFlow.objects.all()
    template_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# -----------------------------------------------------------------------------------
# ---- F L O W S --------------------------------------------------------------------
# -----------------------------------------------------------------------------------

def create_flow(request):
    """
    Creates a new CaptureFlow with a given name
    :param request: flowName
    :return:
    """
    flow_name = request.POST.get("flowName")
    exists = CaptureFlow.objects.filter(name=flow_name)

    if len(exists) == 0:
        capture_flow = CaptureFlow()
        capture_flow.name = flow_name
        capture_flow.save()

    return HttpResponse(status=200)


def delete_flow(request, pk):
    """
    Delete a specific flow
    :param request: /
    :param pk: ID of CaptureFlow
    :return: reloads same page
    """
    #TODO also delete mappings
    flow = CaptureFlow.objects.get(pk=pk)
    flow.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def update_flow(request, pk):
    """
    Connects a list of ConfigCaptures with a CaptureFlow
    :param request: configList -> a list of ConfigCapture-Ids, the order is important!
    :param pk: ID of CaptureFlow
    :return: statuscode 200
    """
    config_ids = request.GET.getlist('configList[]')

    print("Config-List:", config_ids, " | Flow-ID:", pk)
    for i in range(len(config_ids)):

        try:
            mapping = ConfigMapping.objects.get(flow_id=pk, config_id=config_ids[i])
            mapping.order = i
            mapping.save()

        except ObjectDoesNotExist:
            mapping = ConfigMapping()
            mapping.config_id = config_ids[i]
            mapping.flow_id = pk
            mapping.order = i
            mapping.save()

    # Delete all mappings, which are not present anymore
    ConfigMapping.objects.filter(flow_id=pk).exclude(config__in=config_ids).delete()

    return HttpSuccess()


def update_config_detail(request, pk):
    """
    updates the 'repeats'-value of a ConfigMapping
    :param request: repeats, flow_id
    :param pk: ID of CaptureConfig
    :return:
    """
    print("update_config_detail", pk, request.GET)

    repeats = request.GET.get('repeats')
    flow_id = request.GET.get('flow_id')

    if repeats and flow_id:
        mapping = ConfigMapping.objects.get(config_id=pk, flow_id=flow_id)
        mapping.repeats = repeats
        mapping.save()
        return HttpSuccess()
    return HttpFailed()


# -----------------------------------------------------------------------------------
# ---- C O N F I G S ----------------------------------------------------------------
# -----------------------------------------------------------------------------------

def create_config(request):
    """
    creates and saves a new CaptureConfig
    :return: form-model or HttpResponse (on POST)
    """
    print("Create Config-Form", request.POST)

    if request.method == 'POST':
        form = CaptureConfigForm(request.POST)

        if form.is_valid():
            description = form.cleaned_data['description']
            iso = form.cleaned_data['iso']
            aperture = form.cleaned_data['aperture']
            exposure = form.cleaned_data['exposure']
            bulb_time = form.cleaned_data['bulb_time']
            image_format = form.cleaned_data['image_format']

            config = CaptureConfig.objects.create(description=description, iso=iso, aperture=aperture,
                                                  exposure=exposure, bulb_time=bulb_time, image_format=image_format)
            config.save()

            return HttpSuccess()

        return HttpFailed()

    # If camera is present, fetch the current settings, otherwise set default values
    fetch = cc.is_camera_present()

    form = CaptureConfigForm().get_form(iso=cc.get_iso(fetch),
                                        aperture=cc.get_aperture(fetch),
                                        exposure=cc.get_exposure(fetch),
                                        image_format=cc.get_image_format(fetch))

    return render(request, 'controller/create_config.html', {'form': form})


# -----------------------------------------------------------------------------------
# ---- XXXXXXXXX --------------------------------------------------------------------
# -----------------------------------------------------------------------------------


def restart_gphoto(request):
    if cc.restart_gphoto():
        return HttpSuccess()
    return HttpFailed()


# -----------------------------------------------------------------------------------
# ---- S T R E A M ------------------------------------------------------------------
# -----------------------------------------------------------------------------------

@start_as_thread
def start_livestream(filename="", crop=""):
    cc.start_livestream(filename, crop)


def start_stream(request):
    """
    This will start a new video-stream
    :param request: record => if set, the video will be captured to the filesystem
                    crop   => if set, the video will be captured as FULL quality,
                              otherwise in MPEG
    :return:
    """
    if MOCK_CAMERA or cc.is_camera_present():
        crop = request.GET.get('crop')
        record = request.GET.get('record')
        filename = ""
        print("start_stream", crop, record)

        if record:
            cc.stop_livestream()
            if crop:
                filename = "{0}/stream_{1:%Y-%m-%d_%H-%M-%S}.mkv".format(
                    FULL_CAPUTRING_PATH[1:], datetime.datetime.now())
            else:
                filename = "{0}/stream_{1:%Y-%m-%d_%H-%M-%S}.mpeg".format(
                    FULL_CAPUTRING_PATH[1:], datetime.datetime.now())

        start_livestream(filename, crop)

        return HttpSuccess({'filename': filename})

    return HttpFailed()


def stop_stream(request):
    cc.stop_livestream()
    return HttpSuccess()


# -----------------------------------------------------------------------------------
# ---- S A V I N G ------------------------------------------------------------------
# -----------------------------------------------------------------------------------


def save_image(config, filename, path, image_format, filepath):
    image = ImageFile()
    if config:
        image.config = config
    image.create_as_full(filename, path, image_format)
    image.save()

    create_thumbnail(filepath)


@start_as_thread
def create_thumbnail(filepath):
    """
    Creates a thumbnail as a background-task
    :param filepath: path to the full image
    """
    os.makedirs(THUMBNAIL_PATH, exist_ok=True)
    try:
        img = cv2.imread(filepath)
        img = cv2.resize(img, (300, 200), interpolation=cv2.INTER_NEAREST)
        cv2.imwrite('{}thumb_{}'.format(THUMBNAIL_PATH, ntpath.basename(filepath)), img)
        print("Thumbnail created!")
    except:
        print("Thumbnail FAILED ", filepath, os.getcwd())
