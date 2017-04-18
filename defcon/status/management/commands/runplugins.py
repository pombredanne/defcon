"""Component commands."""
from django.utils import module_loading
from django.core.management import base

from defcon.status import models


class Command(base.BaseCommand):
    """Run plugins."""

    help = 'Run pluginss'

    def add_arguments(self, _):
        """Add arguments."""
        pass

    def handle(self, *args, **options):
        """Run the command."""
        # TODO: add filters by components and plugins.
        for component_obj in models.Component.objects.all():
            for plugin_obj in component_obj.plugins.all():
                self.run_plugin(component_obj, plugin_obj)

    def run_plugin(self, component_obj, plugin_obj):
        """Add a plugin."""
        print('Running %s:%s' % (component_obj.name, plugin_obj.plugin.name))
        plugin_class = module_loading.import_string(plugin_obj.plugin.py_module)
        plugin = plugin_class(plugin_obj.config)

        statuses = sorted(plugin.statuses().items())
        for status_id, status in statuses:
            status_obj, created = models.Status.objects.update_or_create(
                id=status_id, defaults=status)
            if created:
                plugin_obj.statuses.add(status_obj)

            action = 'Created' if created else 'Updated'
            print('%s %s:%s config' % (action, plugin_obj.plugin.name, status_obj.title))