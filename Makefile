WEBMIN_FW_TCP_INCOMING = 22 80 443 12321

include $(FAB_PATH)/common/mk/turnkey/nginx.mk
include $(FAB_PATH)/common/mk/turnkey/tkl-webcp.mk
include $(FAB_PATH)/common/mk/turnkey.mk
