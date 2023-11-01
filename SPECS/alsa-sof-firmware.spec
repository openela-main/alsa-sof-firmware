# This is a firmware package, so binaries (which are not run on the host)
# in the end package are expected.
%define _binaries_in_noarch_packages_terminate_build   0
%global _firmwarepath  /usr/lib/firmware
%global _xz_opts -9 --check=crc32

%global sof_ver 2.2.5
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
Source10:       sof-rpl-rt711-l0-rt1316-l12-rt714-l3.tplg.gz
BuildRequires:  alsa-topology >= %{tplg_version}
BuildRequires:  alsa-topology-utils >= %{tplg_version}

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

# Extra topology for Dell SKU 0BDA
zcat %{SOURCE10} > firmware/intel/sof-tplg/$(basename %{SOURCE10} .gz)
chmod 0644 firmware/intel/sof-tplg/$(basename %{SOURCE10} .gz)

# use xz compression
find -P firmware/intel/sof -type f -name "*.ri" -exec xz -z %{_xz_opts} {} \;
for f in $(find -P firmware/intel/sof -type l -name "*.ri"); do \
  l=$(readlink "${f}"); \
  d=$(dirname "${f}"); \
  b=$(basename "${f}"); \
  rm "${f}"; \
  pushd "${d}"; \
  ln -svf "${l}.xz" "${b}.xz"; \
  popd; \
done
find -P firmware/intel/sof-tplg  -type f -name "*.tplg" -exec xz -z %{_xz_opts} {} \;

%build
# SST topology files (not SOF related, but it's a Intel hw support
# and this package seems a good place to distribute them
alsatplg -c /usr/share/alsa/topology/hda-dsp/skl_hda_dsp_generic-tplg.conf \
         -o firmware/skl_hda_dsp_generic-tplg.bin
# use xz compression
xz -z %{_xz_opts} firmware/*.bin
chmod 0644 firmware/*.bin.xz

%install
mkdir -p %{buildroot}%{_firmwarepath}
cp -ra firmware/* %{buildroot}%{_firmwarepath}

# gather files and directories
FILEDIR=$(pwd)
pushd %{buildroot}/%{_firmwarepath}
find -P . -name "*.ri.xz" | sed -e '/^.$/d' > $FILEDIR/alsa-sof-firmware.files
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
%{_firmwarepath}/*.bin.xz

# Licence: 3-clause BSD
# .. for files with suffix .tplg
%{_firmwarepath}/intel/sof-tplg/*.tplg.xz

# Licence: SOF (3-clause BSD plus others)
# .. for files with suffix .ri

%files debug -f alsa-sof-firmware.debug-files

%pretrans -p <lua>
path = "%{_firmwarepath}/intel/sof-tplg"
st = posix.stat(path)
if st and st.type == "link" then
  os.remove(path)
end

%changelog
* Fri Jun 30 2023 Jaroslav Kysela <perex@perex.cz> - 2.2.5-2
- add sof-rpl-rt711-l0-rt1316-l12-rt714-l3.tplg for Dell SKU 0BDA
- add xz compression support (with CRC32)
- Update to v2.2.5

* Mon Jan  9 2023 Jaroslav Kysela <perex@perex.cz> - 2.2.4-1
- Update to v2.2.4

* Wed Dec  7 2022 Jaroslav Kysela <perex@perex.cz> - 2.2.3-1
- Update to v2.2.3

* Thu Sep 29 2022 Jaroslav Kysela <perex@perex.cz> - 2.2.2-1
- Update to v2.2.2

* Mon Jun 20 2022 Jaroslav Kysela <perex@perex.cz> - 2.1.1-1
- Update to v2.1.1 + v2.1.1a (topology)

* Mon Dec 20 2021 Jaroslav Kysela <perex@perex.cz> - 1.9.3-2
- Update to v1.9.3

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.8-2
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu Jul 22 2021 Jaroslav Kysela <perex@perex.cz> - 1.8-1
- Update to v1.8

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 1.6.1-5
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Thu Mar 11 2021 Jaroslav Kysela <perex@perex.cz> - 1.6.1-4
- Add SST Skylake HDA topology binary (bug#1933423)

* Fri Mar  5 2021 Jaroslav Kysela <perex@perex.cz> - 1.6.1-3
- Add TGL-H firmware files

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sun Jan  3 2021 Jaroslav Kysela <perex@perex.cz> - 1.6.1-1
- Update to v1.6.1

* Thu Dec 10 2020 Jaroslav Kysela <perex@perex.cz> - 1.6-4
- Update to v1.6 (Dec 9)

* Thu Nov 19 2020 Jaroslav Kysela <perex@perex.cz> - 1.6-3
- Update to v1.6 (Nov 19)

* Wed Oct 14 2020 Jaroslav Kysela <perex@perex.cz> - 1.6-1
- Update to v1.6 (Oct 13)

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jun  1 2020 Jaroslav Kysela <perex@perex.cz> - 1.5-1
- Update to v1.5

* Tue May 12 2020 Jaroslav Kysela <perex@perex.cz> - 1.4.2-6
- Fix the upgrade (make /usr/lib/firmware/intel/sof-tplg directory again)
- Remove the version from all paths

* Thu Apr 30 2020 Jaroslav Kysela <perex@perex.cz> - 1.4.2-5
- Add missing symlink for sof-cfl.ri

* Thu Mar 12 2020 Jaroslav Kysela <perex@perex.cz> - 1.4.2-4
- Add missing symlink for sof-cml.ri

* Mon Mar  2 2020 Jaroslav Kysela <perex@perex.cz> - 1.4.2-3
- Initial version, SOF firmware 1.4.2
