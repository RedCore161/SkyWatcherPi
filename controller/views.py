import datetime
import ntpath
import os
import time
from threading import Thread

import cv2
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic.list import ListView

import SkyWatcherCC.cameraController as cc
from SkyWatcherCC.settings import FULL_CAPUTRING_PATH, THUMBNAIL_PATH
from SkyWatcherCC.views import HttpSuccess, HttpFailed
from controller.forms import CaptureConfigForm, CaptureFlow
from controller.models import ConfigMapping, ImageFile, CaptureConfig


def start_new_thread(func):
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
    :param request: needs iso, aperture, exposure and image_format
    :return: Statuscode 200 or 400 (for ajax)
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
        print("Capturing START!", time.time(), bulb_time)
        if cc.capture_image(path, filename, iso, aperture, exposure, image_format, bulb_time) == 0:
            print("Capturing DONE!", time.time())
            result = {'filepath': path + filename}
            image = ImageFile()
            if config:
                image.config = config
            image.create_as_full(filename, path, image_format)
            image.save()

            create_thumbnail(result['filepath'][1:])

            return HttpSuccess(result)
    return HttpFailed()


@start_new_thread
def create_thumbnail(filepath):

    os.makedirs(THUMBNAIL_PATH, exist_ok=True)

    img = cv2.imread(filepath)
    img = cv2.resize(img, (300, 200), interpolation=cv2.INTER_NEAREST)
    cv2.imwrite('{}thumb_{}'.format(THUMBNAIL_PATH, ntpath.basename(filepath)), img)
    print("Thumbnail created!")


# -----------------------------------------------------------------------------------
# ---- V I E W - C L A S S E S ------------------------------------------------------
# -----------------------------------------------------------------------------------

class CaptureConfigDetail(DetailView):
    model = CaptureConfig

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mapping = ConfigMapping.objects.get(flow_id=self.request.GET.get('flow_id'), config_id=context['object'])
        context['repeats'] = mapping.repeats
        return context


class ConfigGalleryView(ListView):
    model = ConfigMapping
    context_object_name = 'images'
    template_name = 'dummies/dummy_gallery.html'
    object_list = None
    queryset = None

    def get_queryset(self):
        return ImageFile.objects.filter(config_id=self.kwargs['pk'])


class ConfigMappingListView(ListView):
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
            #print("Q-others: ", others)

            context['other_configs'] = others

        return context


class CaptureFlowListView(ListView):
    model = CaptureFlow
    context_object_name = 'list_flows'
    queryset = CaptureFlow.objects.all()
    template_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return context


# -----------------------------------------------------------------------------------
# ---- F L O W S --------------------------------------------------------------------
# -----------------------------------------------------------------------------------

def create_flow(request):
    flow_name = request.POST.get("flowName")
    exists = CaptureFlow.objects.filter(name=flow_name)

    if len(exists) == 0:
        capture_flow = CaptureFlow()
        capture_flow.name = flow_name
        capture_flow.save()

    return HttpResponse(status=200)


def delete_flow(request, pk):
    #TODO also delete mappings
    print("Pk", pk)
    flow = CaptureFlow.objects.get(pk=pk)
    flow.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def update_flow(request, pk):
    config_ids = request.GET.getlist('configList[]')

    print("Config-List:", config_ids, " | Flow-ID:", pk)
    for i in range(len(config_ids)):

        try:
            mapping = ConfigMapping.objects.get(flow_id=pk, config_id=config_ids[i])
            mapping.order = i
            mapping.save()
            #print("UPDATED", config_ids[i], mapping.config_id, i)

        except ObjectDoesNotExist:
            mapping = ConfigMapping()
            mapping.config_id = config_ids[i]
            mapping.flow_id = pk
            mapping.order = i
            mapping.save()
            #print("CREATED:", config_ids[i], pk, i)

    # Delete all mappings, which are not present anymore
    ConfigMapping.objects.filter(flow_id=pk).exclude(config__in=config_ids).delete()

    return HttpSuccess()


def update_config_detail(request, pk):

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

#TODO OUTDATED
def get_last_images():
    """
    :return: last 5 images
    """
    last_images = ImageFile.objects.order_by('-id')[:5]
    image_list = []
    for image in last_images:
        path = image.path+image.filename
        image_list.append(path)
    return image_list


def create_config(request):

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

@start_new_thread
def start_as_thread():
    cc.start_livestream()


def start_stream(request):
    if cc.is_camera_present():
        start_as_thread()
        return HttpSuccess()
    return HttpFailed()


def stop_stream(request):
    if cc.is_camera_present():
        cc.stop_livestream()
        return HttpSuccess()
    return HttpFailed()
