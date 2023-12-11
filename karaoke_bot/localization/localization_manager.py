class LocalizationManager:
    def __init__(self, local_dict: dict, default_lg_code: str = 'en'):
        self.local_dict = local_dict
        self.default_lg_code = default_lg_code

    # TODO переписать код без метода localize_text в new_karaoke.py, order_track.py. Использовать новые методы снизу
    def localize_text(self, obj_name: str, lg_code: str, params: list) -> str:
        loc_dict = self.local_dict.get(obj_name)
        if loc_dict is not None:
            for key in params:
                if key not in loc_dict:
                    raise KeyError(f'{obj_name}: Key "{key}" is not in {loc_dict}')

                loc_dict = loc_dict[key]

            return loc_dict.get(lg_code, loc_dict[self.default_lg_code])

        raise KeyError(f'Key "{obj_name}" is not in local_text')

    def get_local_obj(self, obj_name: str, keys: list | None = None) -> dict:
        obj_dict = self.local_dict.get(obj_name)
        if obj_dict is not None:
            if keys is not None:
                obj_dict = self.get_nested_value(obj_dict, keys, obj_name)
            return obj_dict

        raise KeyError(f'Key "{obj_name}" is not in local_text')

    @staticmethod
    def get_nested_value(obj_dict: dict, keys: list, obj_name: str) -> dict:
        for key in keys:
            if key not in obj_dict:
                raise KeyError(f'{obj_name}: Key "{key}" is not in {obj_dict}')
            obj_dict = obj_dict[key]
        return obj_dict

    def get_local_value(self, obj_name: str, lg_code: str, params: list) -> str:
        loc_dict = self.get_local_obj(obj_name, params)
        return loc_dict.get(lg_code, loc_dict[self.default_lg_code])
