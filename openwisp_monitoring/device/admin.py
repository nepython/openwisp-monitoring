import uuid

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from nested_admin.nested import (
    NestedBaseGenericInlineFormSet,
    NestedGenericStackedInline,
    NestedModelAdmin,
    NestedStackedInline,
)
from swapper import load_model

from openwisp_controller.config.admin import DeviceAdmin as BaseDeviceAdmin
from openwisp_controller.config.models import Device
from openwisp_utils.admin import TimeReadonlyAdminMixin

from ..monitoring.admin import MetricAdmin
from . import settings as app_settings

DeviceData = load_model('device_monitoring', 'DeviceData')
DeviceMonitoring = load_model('device_monitoring', 'DeviceMonitoring')
AlertSettings = load_model('monitoring', 'AlertSettings')
Chart = load_model('monitoring', 'Chart')
Metric = load_model('monitoring', 'Metric')
Notification = load_model('openwisp_notifications', 'Notification')


class MetricInlineFormSet(NestedBaseGenericInlineFormSet):
    def full_clean(self):
        for form in self.forms:
            obj = form.instance
            if not obj.content_type or not obj.object_id:
                setattr(
                    form.instance,
                    self.ct_field.get_attname(),
                    ContentType.objects.get_for_model(self.instance).pk,
                )
                setattr(form.instance, self.ct_fk_field.get_attname(), self.instance.pk)
        super().full_clean()


class NotificationInline(NestedGenericStackedInline):
    model = Notification
    extra = 0
    max_num = 0
    ct_field = 'actor_content_type'
    ct_fk_field = 'actor_object_id'
    sortable_options = dict()
    readonly_fields = ['message']
    fields = ['message']

    def has_add_permission(self, request, obj=None):
        return False


class AlertSettingsInline(TimeReadonlyAdminMixin, NestedStackedInline):
    model = AlertSettings
    extra = 0
    max_num = 0
    sortable_options = dict()

    def has_add_permission(self, request, obj=None):
        return False


class MetricInline(NestedGenericStackedInline):
    model = Metric
    extra = 0
    formset = MetricInlineFormSet
    inlines = [NotificationInline, AlertSettingsInline]
    readonly_fields = ['name']
    fields = ['name']

    def has_add_permission(self, request, obj=None):
        return False


class DeviceAdmin(BaseDeviceAdmin, NestedModelAdmin):
    def get_extra_context(self, pk=None):
        ctx = super().get_extra_context(pk)
        if pk:
            device_data = DeviceData(pk=uuid.UUID(pk))
            api_url = reverse('monitoring:api_device_metric', args=[pk])
            ctx.update(
                {
                    'device_data': device_data.data_user_friendly,
                    'api_url': api_url,
                    'default_time': Chart.DEFAULT_TIME,
                    'MAC_VENDOR_DETECTION': app_settings.MAC_VENDOR_DETECTION,
                }
            )
        return ctx

    def health_status(self, obj):
        return format_html(
            mark_safe('<span class="health-{0}">{1}</span>'),
            obj.monitoring.status,
            obj.monitoring.get_status_display(),
        )

    health_status.short_description = _('health status')

    def get_form(self, request, obj=None, **kwargs):
        """
        Adds the help_text of DeviceMonitoring.status field
        """
        health_status = DeviceMonitoring._meta.get_field('status').help_text
        kwargs.update(
            {'help_texts': {'health_status': health_status.replace('\n', '<br>')}}
        )
        return super().get_form(request, obj, **kwargs)


# This attribute needs to be set for nested inline
for i, inline in enumerate(DeviceAdmin.inlines):
    DeviceAdmin.inlines[i].sortable_options = dict()

DeviceAdmin.inlines += [MetricInline]

DeviceAdmin.Media.js += MetricAdmin.Media.js + ('monitoring/js/percircle.js',)
DeviceAdmin.Media.css['all'] += (
    'monitoring/css/percircle.css',
) + MetricAdmin.Media.css['all']

DeviceAdmin.list_display.insert(
    DeviceAdmin.list_display.index('config_status'), 'health_status'
)
DeviceAdmin.list_select_related += ('monitoring',)
DeviceAdmin.list_filter.insert(
    0, 'monitoring__status',
)
DeviceAdmin.fields.insert(DeviceAdmin.fields.index('last_ip'), 'health_status')
DeviceAdmin.readonly_fields.append('health_status')

admin.site.unregister(Device)
admin.site.register(Device, DeviceAdmin)
