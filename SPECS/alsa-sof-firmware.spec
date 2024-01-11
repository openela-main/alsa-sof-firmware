# This is a firmware package, so binaries (which are not run on the host)
# in the end package are expected.
%define _binaries_in_noarch_packages_terminate_build   0
%global _firmwarepath  /usr/lib/firmware

%global sof_ver 2.2.4
#global sof_ver_pre rc2
%global sof_ver_rel %{?sof_ver_pre:.%{sof_ver_pre}}
%global sof_ver_pkg v%{sof_ver}%{?sof_ver_pre:-%{sof_ver_pre}}

%global with_sof_addon 0
%global sof_ver_addon 0

%global tplg_version 1.2.4

Summary:        Firmware and topology files for Sound Open Firmware project
Name:           alsa-sof-firmware
Version:        %{sof_ver}
Release:        2%{?sof_ver_rel}%{?dist}
# See later in the spec for a breakdown of licensing
License:        BSD
URL:            https://github.com/thesofproject/sof-bin
Source:         https://github.com/thesofproject/sof-bin/releases/download/%{sof_ver_pkg}/sof-bin-%{sof_ver_pkg}.tar.gz
%if 0%{?with_sof_addon}
Source2:        https://github.com/thesofproject/sof-bin/releases/download/v%{sof_ver_addon}/sof-tplg-v%{sof_ver_addon}.tar.gz
%endif
Source10:       skl_hda_dsp_generic-tplg.bin

# noarch, since the package is firmware
BuildArch:      noarch

%description
This package contains the firmware binaries for the Sound Open Firmware project.

%package debug
Requires:       alsa-sof-firmware
Summary:        Debug files for Sound Open Firmware project
License:        BSD

%description debug
This package contains the debug files for the Sound Open Firmware project.

%prep
%autosetup -n sof-bin-%{sof_ver_pkg}

mkdir -p firmware/intel/sof

# we have the version in the package name
mv sof-%{sof_ver_pkg}/* firmware/intel/sof

# move topology files
mv sof-tplg-%{sof_ver_pkg} firmware/intel/sof-tplg

%if 0%{?with_sof_addon}
tar xvzf %{SOURCE2}
mv sof-tplg-v%{sof_ver_addon}/*.tplg firmware/intel/sof-tplg
%endif

# remove NXP firmware files
rm LICENCE.NXP
rm -rf firmware/intel/sof-tplg/sof-imx8*

# remove Mediatek firmware files
rm -rf firmware/intel/sof-tplg/sof-mt8*

# SST topology files (not SOF related, but it's a Intel hw support
# and this package seems a good place to distribute them
cp %{SOURCE10} firmware/skl_hda_dsp_generic-tplg.bin

%build

%install
mkdir -p %{buildroot}%{_firmwarepath}
cp -ra firmware/* %{buildroot}%{_firmwarepath}

# gather files and directories
FILEDIR=$(pwd)
pushd %{buildroot}/%{_firmwarepath}
find -P . -name "*.ri" | sed -e '/^.$/d' > $FILEDIR/alsa-sof-firmware.files
#find -P . -name "*.tplg" | sed -e '/^.$/d' >> $FILEDIR/alsa-sof-firmware.files
find -P . -name "*.ldc" | sed -e '/^.$/d' > $FILEDIR/alsa-sof-firmware.debug-files
find -P . -type d | sed -e '/^.$/d' > $FILEDIR/alsa-sof-firmware.dirs
popd
sed -i -e 's:^./::' alsa-sof-firmware.{files,debug-files,dirs}
sed -i -e 's!^!/usr/lib/firmware/!' alsa-sof-firmware.{files,debug-files,dirs}
sed -e 's/^/%%dir /' alsa-sof-firmware.dirs >> alsa-sof-firmware.files
cat alsa-sof-firmware.files

%files -f alsa-sof-firmware.files
%license LICENCE*
%doc README*
%dir %{_firmwarepath}

# Licence: 3-clause BSD
%{_firmwarepath}/*.bin

# Licence: 3-clause BSD
# .. for files with suffix .tplg
%{_firmwarepath}/intel/sof-tplg

# Licence: SOF (3-clause BSD plus others)
# .. for files with suffix .ri

%files debug -f alsa-sof-firmware.debug-files

%changelog
* Mon Jan  9 2023 Jaroslav Kysela <perex@perex.cz> - 2.2.4-2
- Update to v2.2.4

* Wed Dec  7 2022 Jaroslav Kysela <perex@perex.cz> - 2.2.3-1
- Update to v2.2.3

* Thu Sep 29 2022 Jaroslav Kysela <perex@perex.cz> - 2.2.2-1
- Update to v2.2.2

* Mon Jun 20 2022 Jaroslav Kysela <perex@perex.cz> - 2.1.1-1
- Update to v2.1.1 + v2.1.1a (topology)

* Wed May 11 2022 Jaroslav Kysela <perex@perex.cz> - 1.9.3-3
- Add sof-adl-rt711-l2-rt1316-l01.tplg topology file

* Thu Dec 16 2021 Jaroslav Kysela <perex@perex.cz> - 1.9.3-1
- Update to v1.9.3

* Tue Nov 23 2021 Jaroslav Kysela <perex@perex.cz> - 1.9.2-1
- Update to v1.9.2

* Tue Oct 26 2021 Jaroslav Kysela <perex@perex.cz> - 1.9-1
- Update to v1.9

* Thu Jul 22 2021 Jaroslav Kysela <perex@perex.cz> - 1.8-1
- Update to v1.8
- Add SST Skylake HDA topology binary

* Sun Jan  3 2021 Jaroslav Kysela <perex@perex.cz> - 1.6.1-1
- Update to v1.6.1

* Thu Dec 10 2020 Jaroslav Kysela <perex@perex.cz> - 1.6-2
- Update to v1.6 (Dec 9)

* Wed Nov 11 2020 Jaroslav Kysela <perex@perex.cz> - 1.6-1
- Update to v1.6 (Oct 13)

* Mon Jun  8 2020 Jaroslav Kysela <perex@perex.cz> - 1.5-2
- Update to v1.5

* Tue Apr 21 2020 Jaroslav Kysela <perex@perex.cz> - 1.4.2-2
- Initial version (Open Sound Firmware v1.4.2)
