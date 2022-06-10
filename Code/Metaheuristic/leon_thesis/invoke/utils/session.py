# import sys
# import requests
# import socket
# from alfa_sdk.common.session import Session
#
#
# class HTTPAdapterWithSocketOptions(requests.adapters.HTTPAdapter):
#     def __init__(self, *args, **kwargs):
#         self.socket_options = kwargs.pop("socket_options", None)
#         # super(HTTPAdapterWithSocketOptions, self).__init__(*args, **kwargs)
#
#     def init_poolmanager(self, *args, **kwargs):
#         if self.socket_options is not None:
#             kwargs["socket_options"] = self.socket_options
#         super(HTTPAdapterWithSocketOptions, self).init_poolmanager(*args, **kwargs)
#
# def init_session():
#     adapter = HTTPAdapterWithSocketOptions(socket_options=get_keepalive_socket_options())
#
#     session = Session()
#     session.http_session.mount("http://", adapter)
#     session.http_session.mount("https://", adapter)
#
#     return session
#
#
# def get_keepalive_socket_options():
#     options = []
#     platform = sys.platform
#     has_tcp_attributes = (
#         hasattr(socket, "TCP_KEEPIDLE")
#         and hasattr(socket, "TCP_KEEPINTVL")
#         and hasattr(socket, "TCP_KEEPCNT")
#     )
#
#     # Linux
#     if platform == "linux" and has_tcp_attributes:
#         options.append((socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1))
#         options.append((socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10))
#         options.append((socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10))
#         options.append((socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 10))
#
#     # MacOS
#     elif platform == "darwin":
#         options.append((socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1))
#         # options.append((socket.IPPROTO_TCP, socket.TCP_KEEPALIVE, 10))
#
#     # Windows
#     elif platform == "win32":
#         # windows requires `sock.ioctl`, whereas requests only support `sock.setsockopt`
#         # conn.sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, TCP_KEEP_IDLE * 1000, TCP_KEEPALIVE_INTERVAL * 1000))
#         pass
#
#     return options