# 永远的七日之都：安卓单包离线工程

> 永远的七日之都是我最喜欢的二游，没有遇上好运营的它永远的遗憾，我希望即使哪天网易彻底放弃了这个项目，我也能回交界都市看看。

从官方原 APK 执行单一构建命令，生成可安装的离线 APK。
本地服务随安装包启动，自动建立本地身份并保存进度。
项目在开发过程中受到 Project7 启发。

- 神器使、服装和影装收藏目标：**140 / 494 / 1900**。
- 保留原版角色界面、模型、换装、剧情、战斗和抽卡动画；初遇池从公开菜单隐藏。
- 普通混合池、影装池及历史池沿用原版界面，本地处理抽卡和结算。
- 手机终端（BBS）第二页提供“背包编辑”：查询道具、设置或增加数量、修改货币及生成影装；
  其中“卡池开关”管理白夜馆历史卡池。历史池默认全部关闭，最多同时开启 12 个，
  有未完成抽卡的卡池始终可进入；修改后重新进入白夜馆生效。
- 素材优先从官方 CDN 下载，按固定大小与 SHA-256 校验并缓存；备用 HTTPS 素材源
  和本地资源 ZIP 可在首次准备页面配置。资源完整后可断网运行。

## 环境准备

需要 Python **3.12**、JDK 17、Android SDK（platform 32 + build-tools 37.0），
外加一份官方原 APK。以下按顺序装。

### Python 3.12 与依赖

```sh
# macOS
brew install python@3.12

# 或已装 uv
uv python install 3.12

# Debian / Ubuntu 24.04 自带；22.04 加 deadsnakes PPA
sudo apt install python3.12 python3.12-venv

python3.12 -m venv .venv
.venv/bin/pip install -r requirements-offline.txt
```

装的是 lz4、xdis、pymongo、androguard 四个包，其中 `xdis==6.1.8` 决定上限：
3.14 上装不出可用发行版，换 6.3.0 又会算出不同的字节码、构建在
`Unrelated init module body changed` 处停下。3.12 是实测能完整构建的版本。

### JDK 17

```sh
# macOS
brew install openjdk@17
export JAVA_HOME="$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home"

# Debian / Ubuntu
sudo apt install openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

`$JAVA_HOME/bin` 下要有 `java`、`javac`、`keytool`，构建脚本会逐个检查。

### Android SDK

```sh
# macOS：命令行工具
brew install --cask android-commandlinetools
export ANDROID_HOME="$HOME/Library/Android/sdk"

# Linux：解压 commandlinetools 后
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

sdkmanager --licenses
sdkmanager "platforms;android-32" "build-tools;37.0.0"
```

装完确认这三个文件存在：

```sh
ls "$ANDROID_HOME/build-tools/37.0.0/zipalign" \
   "$ANDROID_HOME/build-tools/37.0.0/lib/d8.jar" \
   "$ANDROID_HOME/build-tools/37.0.0/lib/apksigner.jar" \
   "$ANDROID_HOME/platforms/android-32/android.jar"
```

### 官方原 APK

从官方渠道取得 1.96.455（versionCode 10960455），然后校验：

```sh
shasum -a 256 /path/to/original.apk
# 必须等于 12e57f77059f7f3964585f3a615410f3f9625101d885883cd4de4397f490c503
```

### 把 JDK 与 SDK 接到默认路径

构建脚本默认在 `toolchains/` 下找 JDK、build-tools 和 `android.jar`。做三个软链，
之后就不用每次传参数：

```sh
mkdir -p toolchains/java/jdk-17.0.21+9/Contents \
         toolchains/build-tools toolchains/android-sdk/platforms
ln -sfn "$JAVA_HOME" toolchains/java/jdk-17.0.21+9/Contents/Home
ln -sfn "$ANDROID_HOME/build-tools/37.0.0" toolchains/build-tools/android-37.0
ln -sfn "$ANDROID_HOME/platforms/android-32" toolchains/android-sdk/platforms/android-32
```

不想做软链也可以分别传 `--java-home`、`--build-tools`、`--android-jar`。

## 一条命令生成 APK

```sh
.venv/bin/python tools/build_offline_project.py /path/to/original.apk
```

产物写在原包旁边，文件名是原包名加 `-offline.apk`。构建过程只读原 APK。

可选参数都有默认值，按需追加：

| 参数 | 默认 | 用途 |
|---|---|---|
| `--output` | 原包旁 `-offline.apk` | 指定产物路径 |
| `--build-dir` | `.offline-build/` | 构建缓存、签名材料、中间产物 |
| `--render-mode` | `astc` | `png` 走原版 PNG 界面兼容路径 |
| `--backend` | `project7` | `legacy` 是保留的对照后端 |
| `--java-home` / `--build-tools` / `--android-jar` | `toolchains/` 内 | 指向本机 JDK 17 与 Android SDK |
| `--component-offline-input` | 自动发现 | 纯源码包指定固定 Project7 组件 zip |
| `--offline` | 关 | 仅约束 legacy 的 `script.npk` 缓存；Project7 脚本重建始终本地 |

### 签名怎么控制

签名身份只由构建参数决定，产物就是那把钥匙签出来的。

| 参数 | 作用 |
|---|---|
| 不传 `--keystore` | 使用 `build-dir` 内的开发密钥 `signing/offline-dev.p12`，密码首次构建随机写入同目录 `password.txt`（0600）。默认 `build-dir` 是 `.offline-build/`，所以同一缓存连续构建的证书不变；换目录即换钥匙 |
| `--keystore <p12>` | 指定已有密钥，必须同时给 `--key-password-env <变量名>`，密码从该环境变量读；文件缺失或变量为空直接报错 |
| `--key-alias` | 默认 `forever7-local`；自动生成的密钥为 PKCS12 / RSA 2048 / 3650 天 / `CN=Forever7 Local Development` |
| `--expected-cert-sha256` | 发布前比对证书指纹，不匹配即失败，用于锁定固定签名身份 |

Android 只允许同证书覆盖安装：用另一把钥匙构建的 APK 需要先卸载旧包（会清掉本机
存档），或者用同一 `--keystore`／同一 `build-dir` 重建。

固定原包：网易 Android **1.96.455 / 10960455**，SHA-256：
`12e57f77059f7f3964585f3a615410f3f9625101d885883cd4de4397f490c503`。
固定 Project7 组件随仓库提供（`vendor/project7/component-v2.10.1.zip`，
57,258,978 字节），哈希在 `upstream/project7/component.json` 里校验。
构建过程只读原 APK，输出写入指定位置。

源码目录职责见 [目录说明](README-offline-project.md)；
最终功能验收见 `reports/offline-inventory-v23-acceptance.json` 与
`reports/offline-acceptance-v1.json`。源代码包排除原 APK、完整素材、私人存档、
签名私钥和工具链。
