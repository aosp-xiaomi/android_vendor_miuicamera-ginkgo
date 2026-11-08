#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from the proprietary version
include vendor/miuicamera-ginkgo/xiaomi/BoardConfigVendor.mk

MIUICAMERA_PATH := vendor/miuicamera-ginkgo

# Properties
TARGET_SYSTEM_PROP += $(MIUICAMERA_PATH)/system.prop

# Sepolicy
BOARD_VENDOR_SEPOLICY_DIRS += $(MIUICAMERA_PATH)/sepolicy/vendor
