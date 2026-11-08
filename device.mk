#
# SPDX-License-Identifier: Apache-2.0
#

MIUICAMERA_PATH := vendor/miuicamera-ginkgo

# Inherit from the proprietary version
$(call inherit-product, $(MIUICAMERA_PATH)/xiaomi/xiaomi-vendor.mk)

# Priv-app permission
PRODUCT_COPY_FILES += \
    $(MIUICAMERA_PATH)/configs/privapp-permissions-miuicamera.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/privapp-permissions-miuicamera.xml

# Shared libraries required by the app (cloud-common.jar, zxing.jar)
PRODUCT_COPY_FILES += \
    $(MIUICAMERA_PATH)/configs/miuicamera-cloud-common.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/miuicamera-cloud-common.xml

# Soong namespaces
PRODUCT_SOONG_NAMESPACES += \
    $(MIUICAMERA_PATH)

# Sysconfig (hidden API allowlist)
PRODUCT_COPY_FILES += \
    $(MIUICAMERA_PATH)/configs/miuicamera-hiddenapi-package-allowlist.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/sysconfig/miuicamera-hiddenapi-package-allowlist.xml
