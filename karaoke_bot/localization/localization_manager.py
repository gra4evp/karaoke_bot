class LocalizationManager:
    def __init__(self, local_dict: dict, default_lg_code: str = 'en'):
        self.local_dict = local_dict
        self.default_lg_code = default_lg_code

    def localize_text(self, obj_name: str, lg_code: str, params: list):
        obj_text = self.local_dict.get(obj_name)
        if obj_text is not None:
            for key in params:
                if key not in obj_text:
                    raise KeyError(f'{obj_name}: Key "{key}" is not in {obj_text}')

                obj_text = obj_text[key]

            return obj_text.get(lg_code, obj_text[self.default_lg_code])

        raise KeyError(f'Key "{obj_name}" is not in local_text')