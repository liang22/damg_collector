; �ýű�ʹ�� HM VNISEdit �ű��༭���򵼲���

; ��װ�����ʼ���峣��
!define PRODUCT_NAME "DAMG Collector"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER "eCloudTech, Inc."
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\run_stable.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; ------ MUI �ִ����涨�� (1.67 �汾���ϼ���) ------
!include "MUI.nsh"

; MUI Ԥ���峣��
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; ��ӭҳ��
!insertmacro MUI_PAGE_WELCOME
; ��װ����ҳ��
!insertmacro MUI_PAGE_INSTFILES
; ��װ���ҳ��
!define MUI_FINISHPAGE_RUN "C:\damg\bin\create_wmconcat.bat"
!insertmacro MUI_PAGE_FINISH

; ��װж�ع���ҳ��
!insertmacro MUI_UNPAGE_INSTFILES

; ��װ�����������������
!insertmacro MUI_LANGUAGE "SimpChinese"

; ��װԤ�ͷ��ļ�
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; ------ MUI �ִ����涨����� ------

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
 *  �����ǰ�װ�����ж�ز���  *
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

#-- ���� NSIS �ű��༭�������� Function ���α�������� Section ����֮���д���Ա��ⰲװ�������δ��Ԥ֪�����⡣--#

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "��ȷʵҪ��ȫ�Ƴ� $(^Name) ���������е������" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) �ѳɹ��ش���ļ�����Ƴ���"
FunctionEnd
