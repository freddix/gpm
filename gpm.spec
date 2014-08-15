Summary:	General Purpose Mouse support for Linux
Name:		gpm
Version:	1.20.7
Release:	1
Epoch:		1
License:	GPL v2+
Group:		Daemons
Source0:	http://www.nico.schottelius.org/software/gpm/archives/%{name}-%{version}.tar.lzma
# Source0-md5:	fa8a6fe09826896625ca557ac5e42ed7
Source1:	%{name}.sysconfig
Source2:	%{name}.service
Patch0:		%{name}-DESTDIR.patch
Patch1:		%{name}-gawk.patch
Patch2:		%{name}-nodebug.patch
Patch3:		%{name}-dont_display_stupid_error_messages.patch
URL:		http://linux.schottelius.org/gpm/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	gawk
BuildRequires:	ncurses-devel
BuildRequires:	texinfo
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}
Requires(post,preun,postun):	systemd-units
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
GPM adds mouse support to text-based Linux applications such as emacs,
Midnight Commander, and more. It also provides console cut-and-paste
operations using the mouse. Includes a program to allow pop-up menus
to appear at the click of a mouse button.

%package libs
Summary:	GPM libraries
Group:		Libraries
Provides:	libgpm.so.1

%description libs
This package contains library files neccessary to run most of
mouse-aware applications.

%package devel
Summary:	Header files and documentation for writing mouse driven programs
Group:		Development/Libraries
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}

%description devel
This package allows you to develop your own text-mode programs that
take advantage of the mouse.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%{__sed } -i 's#/usr##' doc/manpager
cat configure.ac.footer >> configure.ac

%build
mkdir config
./autogen.sh
%{__libtoolize}
%{__aclocal} -I config
%{__autoheader}
%{__autoconf}
%configure \
	--disable-static    \
	--with-curses
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/sysconfig

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/sysconfig/mouse
install -D %{SOURCE2} $RPM_BUILD_ROOT%{systemdunitdir}/gpm.service
# SONAME was bumped because of incompatibility with Debian libgpm.so.1
# (which in turn was incompatible with libgpm.so.1 from the rest of the world)
# We can leave compatibility symlink as we didn't have ABI break recently
ln -s libgpm.so.2.1.0 $RPM_BUILD_ROOT%{_libdir}/libgpm.so.1

# for rpm autodeps
chmod +x $RPM_BUILD_ROOT%{_libdir}/libgpm.so.*

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post gpm.service
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%preun
%systemd_preun gpm.service

%postun
%systemd_postun
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%post	libs -p /usr/sbin/ldconfig
%postun	libs -p /usr/sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README TODO doc/FAQ doc/README* conf/*.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/mouse
%{systemdunitdir}/gpm.service

%attr(755,root,root) %{_bindir}/disable-paste
%attr(755,root,root) %{_bindir}/display-buttons
%attr(755,root,root) %{_bindir}/display-coords
%attr(755,root,root) %{_bindir}/get-versions
%attr(755,root,root) %{_bindir}/gpm-root
%attr(755,root,root) %{_bindir}/hltest
%attr(755,root,root) %{_bindir}/mev
%attr(755,root,root) %{_bindir}/mouse-test
%attr(755,root,root) %{_sbindir}/gpm

%{_infodir}/gpm.info*
%{_mandir}/man1/gpm-root.1*
%{_mandir}/man1/mev.1*
%{_mandir}/man1/mouse-test.1*
%{_mandir}/man7/gpm-types.7*
%{_mandir}/man8/gpm.8*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %ghost %{_libdir}/libgpm.so.2
%attr(755,root,root) %{_libdir}/libgpm.so.*.*.*
%attr(755,root,root) %{_libdir}/libgpm.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libgpm.so
%{_includedir}/gpm.h

