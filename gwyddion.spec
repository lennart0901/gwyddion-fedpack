# Optional features:
#   --with-kde4-thumbnailer    Enables the kde4-thumbnailer subpackage (and
#                              introduces lots of new dependencies).
%define enable_kde4_thumbnailer %{?_with_kde4_thumbnailer:1}%{!?_with_kde4_thumbnailer:0}

Name:          gwyddion
Version:       2.30
Release:       2
Summary:       An SPM data visualization and analysis tool

Group:         Applications/Engineering
License:       GPLv2+
URL:           http://gwyddion.net/
Source0:       http://gwyddion.net/download/%{version}/%{name}-%{version}.tar.xz
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(id -un)
Requires(pre):    /sbin/ldconfig
Requires(postun): /sbin/ldconfig

# applied in SVN trunk rev. 14452
Patch0: gwyddion-utf8-and-fsf.patch
# From upstream / applied in SVN trunk
Patch1: gwyddion-2.30-color-button-debris-crash.patch

BuildRequires: gtk2-devel >= 2.8
BuildRequires: gtkglext-devel
BuildRequires: libxml2-devel
BuildRequires: zlib-devel
BuildRequires: gettext
BuildRequires: desktop-file-utils >= 0.9
BuildRequires: pkgconfig
BuildRequires: findutils
BuildRequires: libXmu-devel
BuildRequires: minizip-devel
BuildRequires: fftw-devel >= 3.1
BuildRequires: perl >= 5.005
BuildRequires: sed
BuildRequires: gtksourceview2-devel
BuildRequires: pygtk2-devel
BuildRequires: python2-devel >= 2.2

%if %{enable_kde4_thumbnailer}
BuildRequires: kdelibs-devel >= 4.0
%endif

# The only packaged perl module is private, don't expose it.
%global __perl_provides %{nil}

%global pkglibdir %{_libdir}/%{name}
%global pkglibexecdir %{_libexecdir}/%{name}
%global pkgdatadir %{_datadir}/%{name}
%global pkgincludedir %{_includedir}/%{name}
%global gtkdocdir %{_datadir}/gtk-doc/html
%global gconfdir %{_sysconfdir}/gconf/schemas

%global schemas %{gconfdir}/gwyddion-thumbnailer.schemas

%package pygwy
Summary: Gwyddion module with embedded python
Requires: %{name}%{?_isa} = %{version}-%{release}

%package devel
Summary: Headers, libraries and tools for Gwyddion module development
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires:      gtk2-devel >= 2.8
Requires:      gtkglext-devel
Requires:      fftw-devel
Requires:      pkgconfig

%package devel-doc
Summary:       API documentation of Gwyddion
Group:         Documentation

%package perl-plugin-module
Summary: Perl module to read Gwyddion dump files used in plug-ins
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: perl

%package python-plugin-module
Summary: Python module to read Gwyddion dump files used in plug-ins
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: python2 >= 2.2

%package ruby-plugin-module
Summary: Ruby module to read Gwyddion dump files used in plug-ins
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: ruby

%package thumbnailer-gconf
Summary:         GConf schemas for gwyddion-thumbnailer integration
Group:           System Environment/Libraries
BuildRequires: GConf2
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires(pre):   GConf2
Requires(post):  GConf2
Requires(preun): GConf2


%if %{enable_kde4_thumbnailer}
%package thumbnailer-kde4
Summary:         KDE4 gwyddion thumbnailer module
Group:           System Environment/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
# We do not actually link with them, but they own the module directory.
Requires:        %{kde4libs} >= 4.0
%endif

%description
Gwyddion is a modular SPM (Scanning Probe Microsopy) data visualization and
analysis tool written with Gtk+.

It can be used for all most frequently used data processing operations
including: leveling, false color plotting, shading, filtering, denoising, data
editing, integral transforms, grain analysis, profile extraction, fractal
analysis, and many more.  The program is primarily focused on SPM data analysis
(e.g. data obtained from AFM, STM, NSOM, and similar microscopes).  However, it
can also be used for analysis of SEM (Scanning Electron Microscopy) data or any
other 2D data.

%description pygwy
With the pygwy Gwyddion module Gwyddion modules can be written in Python.

%description devel
Header files, libraries and tools for Gwyddion module development.

%description devel-doc
API documentation for Gwyddion.

%description perl-plugin-module
Perl module to read Gwyddion dump files used in plug-ins.

%description python-plugin-module
Python module to read Gwyddion dump files used in plug-ins.

%description ruby-plugin-module
Ruby module to read Gwyddion dump files used in plug-ins.

%description thumbnailer-gconf
GConf schemas that register gwyddion-thumbnailer as thumbnailer for SPM files
in GNOME and XFce.

%if %{enable_kde4_thumbnailer}
%description thumbnailer-kde4
Gwyddion-thumbnailer based KDE thumbnail creator extension module for SPM
files.
%endif


%prep
%setup -q
# Don't install .la files.
sed -i -e '/# Install the pseudo-library/,/^$/d' ltmain.sh
# Replace universal /usr/bin/env shbang with the real thing.
sed -i -e '1s/env *//' plugins/process/*.{py,rb,pl}
%patch0 -p1
%patch1 -p0

%build
%configure --without-pascal --disable-rpath \
           --without-kde4-thumbnailer %{?_with_kde4_thumbnailer}
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=%{buildroot}

%find_lang %{name}

# Perl, Python, and Ruby modules are private, remove the Perl man page.
rm -f %{buildroot}/%{_mandir}/man3/Gwyddion::dump.*

#remove plugin related stuff
rm -rf %{buildroot}/%{pkglibexecdir}/plugins/*
#rm -rf %{buildroot}/%{pkglibdir}/perl
#rm -rf %{buildroot}/%{pkglibdir}/python
#rm -rf %{buildroot}/%{pkglibdir}/ruby

%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

%post
/sbin/ldconfig
update-mime-database %{_datadir}/mime &>/dev/null || :
update-desktop-database &>/dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
/sbin/ldconfig
update-mime-database %{_datadir}/mime &>/dev/null || :
update-desktop-database &>/dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%pre thumbnailer-gconf
%gconf_schema_prepare %{schemas}

%post thumbnailer-gconf
%gconf_schema_upgrade %{schemas}

%preun thumbnailer-gconf
%gconf_schema_remove %{schemas}


%files -f %{name}.lang
%defattr(755,root,root)
%{_bindir}/%{name}
%{_bindir}/%{name}-thumbnailer
%defattr(-,root,root)
%doc AUTHORS COPYING INSTALL.%{name} NEWS README THANKS
%{pkgdatadir}/pixmaps/*.png
%{pkgdatadir}/pixmaps/*.ico
%dir %{pkgdatadir}/pixmaps
%{pkgdatadir}/gradients/
%{pkgdatadir}/glmaterials/
%{pkgdatadir}/ui/
%dir %{pkgdatadir}
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/%{name}-thumbnailer.1*
%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{pkglibdir}/modules/
%dir %{pkglibdir}
%{_libdir}/*.so.*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/mime/packages/%{name}.xml
%{_datadir}/thumbnailers/%{name}.thumbnailer

%files pygwy
%defattr(-,root,root)
%{pkglibdir}/modules/pygwy.so
%{python_sitearch}/gwy.so
%{pkgdatadir}/pygwy/

%files devel
%defattr(-,root,root)
%doc devel-docs/CODING-STANDARDS
%doc data/%{name}.vim
%{pkgincludedir}/
%{_libdir}/*.so
%{_libdir}/pkgconfig/gwyddion.pc
%{pkglibdir}/include/gwyconfig.h
%dir %{pkglibdir}/include
%dir %{pkglibexecdir}/plugins
%dir %{pkglibexecdir}

%files devel-doc
%defattr(-,root,root)
%doc %{gtkdocdir}
%doc %dir %{_datadir}/gtk-doc

%files perl-plugin-module
%{pkglibdir}/perl
%doc plugins/process/invert_perl.pl

%files python-plugin-module
%{pkglibdir}/python
%doc plugins/process/invert_python.py

%files ruby-plugin-module
%{pkglibdir}/ruby
%doc plugins/process/invert_ruby.rb
%doc plugins/process/invert_narray.rb

%files thumbnailer-gconf
%defattr(-,root,root)
%{gconfdir}/*.schemas

%if %{enable_kde4_thumbnailer}
%files thumbnailer-kde4
%defattr(-,root,root)
%{_libdir}/kde4/gwythumbcreator.so
%endif

%changelog
* Mon Dec 10 2012 Lennart Fricke <lennart.fricke@kabelmail.de> - 2.30-2
- removed commented sections
- split off pygwy
- added icon-cache scriptlets
- added plug-ins

* Sun Dec  9 2012 Lennart Fricke <lennart.fricke@kabelmail.de> - 2.30-1
- modified spec for fedora packaging
