from django.forms.models import model_to_dict


class DefaultView():
    def render(self, object_to_render=None):
        if object_to_render:
            object_dict = model_to_dict(object_to_render)
            return object_dict
        else:
            {}
