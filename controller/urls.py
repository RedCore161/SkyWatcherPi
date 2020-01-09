from django.conf.urls import url
from django.http import StreamingHttpResponse
from django.views.generic import TemplateView

from SkyWatcherCC.camera import VideoCamera, gen
from controller import views

urlpatterns = [

    url(r'^index', TemplateView.as_view(template_name='controller/index.html'), name='index'),
    url(r'^livestream', TemplateView.as_view(template_name='controller/live_stream.html'), name='live_stream'),


    url(r'^captureflow/CREATE', views.create_flow, name='create_flow'),

    url(r'^captureflow/(?P<pk>\d+)/DELETE', views.delete_flow, name='delete_flow'),
    url(r'^captureflow/(?P<pk>\d+)/UPDATE', views.update_flow, name='update_flow'),

    url(r'^captureflow/LIST$',
        views.CaptureFlowListView.as_view(template_name='controller/list_flows.html'), name='load_simple_flows'),
    url(r'^captureflow/(?P<pk>\d+)/DETAIL',
        views.ConfigMappingListView.as_view(template_name='controller/captureflow_detail.html', simple_view=True), name='detail_capture_flow'),

    url(r'^captureflow/SETUP$',
        views.CaptureFlowListView.as_view(template_name='controller/setup_flows.html'), name='setup_flows'),
    url(r'^captureflow/(?P<pk>\d+)/LOAD',
        views.ConfigMappingListView.as_view(template_name='controller/load_capture_flow.html'), name='load_capture_flow'),

    url(r'^captureconfig/ajax/(?P<pk>\d+)/UPDATE', views.update_config_detail, name='update_config_detail'),
    url(r'^captureconfig/ajax/(?P<pk>\d+)/GET', views.CaptureConfigDetail.as_view(), name='get_config_detail'),
    url(r'^captureconfig/CREATE', views.create_config, name='create_config'),

    url(r'^captureconfig/(?P<pk>\d+)/GALLERY', views.ConfigGalleryView.as_view(), name='load_gallery'),
    url(r'^runconfig/(?P<pk>\d+)/PERFORM', views.ConfigGalleryView.as_view(), name='perform_config'),

    url(r'^ajax/captureimage/(?P<config_id>\d+)/WITHCONFIG', views.capture, name='capture_image_with_config'),
    url(r'^ajax/captureimage', views.capture, name='capture_image'),
    url(r'^ajax/restartgphoto', views.restart_gphoto, name='restart_gphoto'),

    url(r'^ajax/startstream', views.start_stream, name='start_stream'),
    url(r'^ajax/stopstream', views.stop_stream, name='stop_stream'),
    url(r'^ajax/monitor', lambda r: StreamingHttpResponse(gen(VideoCamera()),
                                                        content_type='multipart/x-mixed-replace; boundary=frame'),
                                                        name="stream_frame"),
]
