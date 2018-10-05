from typing import Any


def import_mod_part(modpath: str) -> Any:
    """
    Used to manually import module attributes from string

    Parameters
    ----------
    modpath
        Dotted module path for the given attribute

    Returns
    -------
    obj
        Imported object

    Examples
    --------
    Importing various objects::

        cls = import_mod_part('my_namespace.my_module.MyClass')
        attr = import_mod_part('my_namespace.my_module.ATTR')
        fn = import_mod_part('my_namespace.my_module.my_function')
    """
    module_str, cls_str = modpath.rsplit('.', 1)
    module = __import__(module_str, fromlist=[cls_str])
    return getattr(module, cls_str)
