API Reference
=============

Exceptions
----------

.. autoexception:: winappaudiorouter.AudioRoutingError

Data models
-----------

.. autoclass:: winappaudiorouter.AudioDeviceInfo
   :members:

.. autoclass:: winappaudiorouter.AudioSessionInfo
   :members:

Device discovery
----------------

.. autofunction:: winappaudiorouter.list_output_devices

.. autofunction:: winappaudiorouter.list_input_devices

.. autofunction:: winappaudiorouter.find_output_device

.. autofunction:: winappaudiorouter.find_input_device

Session discovery
-----------------

.. autofunction:: winappaudiorouter.list_app_sessions

.. autofunction:: winappaudiorouter.list_input_sessions

.. autofunction:: winappaudiorouter.resolve_process_ids

.. autofunction:: winappaudiorouter.resolve_input_process_ids

Routing
-------

.. autofunction:: winappaudiorouter.set_app_output_device

.. autofunction:: winappaudiorouter.set_app_input_device

.. autofunction:: winappaudiorouter.get_app_output_device

.. autofunction:: winappaudiorouter.get_app_input_device

.. autofunction:: winappaudiorouter.clear_app_output_device

.. autofunction:: winappaudiorouter.clear_app_input_device
