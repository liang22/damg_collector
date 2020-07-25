; 该脚本使用 HM VNISEdit 脚本编辑器向导产生

; 安装程序初始定义常量
!define PRODUCT_NAME "DAMG Collector"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER "eCloudTech, Inc."
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\run_stable.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; ------ MUI 现代界面定义 (1.67 版本以上兼容) ------
!include "MUI.nsh"

; MUI 预定义常量
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; 欢迎页面
!insertmacro MUI_PAGE_WELCOME
; 安装过程页面
!insertmacro MUI_PAGE_INSTFILES
; 安装完成页面
!define MUI_FINISHPAGE_RUN "C:\damg\bin\create_wmconcat.bat"
!insertmacro MUI_PAGE_FINISH

; 安装卸载过程页面
!insertmacro MUI_UNPAGE_INSTFILES

; 安装界面包含的语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装预释放文件
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; ------ MUI 现代界面定义结束 ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "eCloudCLI.DAMG.Windows.stable01.exe"
InstallDir "C:\damg\bin\"
InstallDirRegKey HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "C:\damg\bin\"
  SetOverwrite ifnewer
  File "dist\run_stable.exe"
  CreateDirectory "$SMPROGRAMS\DAMG Collector"
  File "dist\run_single.exe"
  File "dist\run_series.exe"
  File "dist\dam_high_frequency.exe"
  File "dist\dam_collect.exe"
  SetOutPath "C:\damg\etc\"
  File "conf\damg.conf"
  SetOutPath "C:\damg\tools\"
  File "tools\zip.exe"
  File "tools\strings64.exe"
  File "tools\strings.exe"
  File "tools\openssl.exe"
  File "tools\libssl-1_1-x64.dll"
  File "tools\libcrypto-1_1-x64.dll"
  File "tools\bzip2.dll"
  SetOutPath "C:\damg\bin\"
  File "src\create_wmconcat.sql"
  File "src\create_wmconcat.bat"
SectionEnd

Section -AdditionalIcons
  SetOutPath $INSTDIR
  CreateShortCut "$SMPROGRAMS\DAMG Collector\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "C:\damg\bin\run_stable.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "C:\damg\bin\run_stable.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

/******************************
 *  以下是安装程序的卸载部分  *
 ******************************/

Section Uninstall
  Delete "$INSTDIR\uninst.exe"
  Delete "C:\damg\bin\create_wmconcat.bat"
  Delete "C:\damg\bin\create_wmconcat.sql"
  Delete "C:\damg\tools\bzip2.dll"
  Delete "C:\damg\tools\libcrypto-1_1-x64.dll"
  Delete "C:\damg\tools\libssl-1_1-x64.dll"
  Delete "C:\damg\tools\openssl.exe"
  Delete "C:\damg\tools\strings.exe"
  Delete "C:\damg\tools\strings64.exe"
  Delete "C:\damg\tools\zip.exe"
  Delete "C:\damg\conf\damg.conf"
  Delete "C:\damg\bin\dam_collect.exe"
  Delete "C:\damg\bin\dam_high_frequency.exe"
  Delete "C:\damg\bin\run_series.exe"
  Delete "C:\damg\bin\run_single.exe"
  Delete "C:\damg\bin\run_stable.exe"

  Delete "$SMPROGRAMS\DAMG Collector\Uninstall.lnk"
  Delete "$DESKTOP\DAMG Collector.lnk"
  Delete "$SMPROGRAMS\DAMG Collector\DAMG Collector.lnk"

  RMDir "C:\damg\tools\"
  RMDir "C:\damg\conf\"
  RMDir "C:\damg\bin\"
  RMDir "$SMPROGRAMS\DAMG Collector"

  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd

#-- 根据 NSIS 脚本编辑规则，所有 Function 区段必须放置在 Section 区段之后编写，以避免安装程序出现未可预知的问题。--#

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "你确实要完全移除 $(^Name) ，及其所有的组件？" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) 已成功地从你的计算机移除。"
FunctionEnd
