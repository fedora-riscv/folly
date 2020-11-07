# executor_api.h does not seem to get generated
%bcond_without python

# fixed_string_test fails with "error: non-constant condition for static assertion"
%bcond_with tests

%global _static_builddir static_build

Name:           folly
Version:        2020.11.02.00
Release:        2%{?dist}
Summary:        An open-source C++ library developed and used at Facebook

License:        ASL 2.0
URL:            https://github.com/facebook/folly
Source0:        https://github.com/facebook/folly/releases/download/v%{version}/folly-v%{version}.tar.gz
# Honor DESTDIR when installing Python extension
Patch0:         %{name}-py_destdir.patch

# Folly is known not to work on big-endian CPUs
# https://bugzilla.redhat.com/show_bug.cgi?id=1892151
ExcludeArch:    s390x

BuildRequires:  cmake
BuildRequires:  gcc-c++
# Docs dependencies
BuildRequires:  pandoc
# Library dependencies
# for libiberty
BuildRequires:  binutils-devel
BuildRequires:  boost-devel
BuildRequires:  bzip2-devel
BuildRequires:  double-conversion-devel
BuildRequires:  fmt-devel
BuildRequires:  gflags-devel
BuildRequires:  glog-devel
%if %{with tests}
BuildRequires:  gmock-devel
%endif
BuildRequires:  libaio-devel
BuildRequires:  libdwarf-devel
BuildRequires:  libevent-devel
BuildRequires:  libsodium-devel
BuildRequires:  libunwind-devel
# 0.7-3 fixes build on armv7hl
BuildRequires:  liburing-devel >= 0.7-3
BuildRequires:  libzstd-devel
BuildRequires:  lz4-devel
BuildRequires:  openssl-devel
%if %{with python}
BuildRequires:  python3-Cython
BuildRequires:  python3-devel
BuildRequires:  python3-wheel
%endif
BuildRequires:  snappy-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel

%description
Folly (acronymed loosely after Facebook Open Source Library) is a library of
C++14 components designed with practicality and efficiency in mind. Folly
contains a variety of core library components used extensively at Facebook. In
particular, it's often a dependency of Facebook's other open source C++ efforts
and place where those projects can share code.

It complements (as opposed to competing against) offerings such as Boost and of
course std. In fact, we embark on defining our own component only when something
we need is either not available, or does not meet the needed performance
profile. We endeavor to remove things from folly if or when std or Boost
obsoletes them.

Performance concerns permeate much of Folly, sometimes leading to designs that
are more idiosyncratic than they would otherwise be (see e.g. PackedSyncPtr.h,
SmallLocks.h). Good performance at large scale is a unifying theme in all of
Folly.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       binutils-devel%{?_isa}
Requires:       boost-devel%{?_isa}
Requires:       bzip2-devel%{?_isa}
Requires:       cmake-filesystem
Requires:       double-conversion-devel%{?_isa}
Requires:       fmt-devel%{?_isa}
Requires:       glog-devel%{?_isa}
Requires:       gmock-devel%{?_isa}
Requires:       libaio-devel%{?_isa}
Requires:       libdwarf-devel%{?_isa}
Requires:       libevent-devel%{?_isa}
Requires:       libsodium-devel%{?_isa}
Requires:       libunwind-devel%{?_isa}
Requires:       liburing-devel%{?_isa} >= 0.7-3
Requires:       libzstd-devel%{?_isa}
Requires:       lz4-devel%{?_isa}
Requires:       openssl-devel%{?_isa}
Requires:       snappy-devel%{?_isa}
Requires:       xz-devel%{?_isa}
Requires:       zlib-devel%{?_isa}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package        docs
Summary:        Documentation for %{name}
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}

%description    docs
The %{name}-docs package contains documentation for %{name}.


%if %{with python}
%package -n python3-%{name}
Summary:        Python bindings for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n python3-%{name}
The python3-%{name} package contains Python bindings for %{name}.
%endif


%package        static
Summary:        Static development libraries for %{name}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}

%description    static
The %{name}-static package contains static libraries for
developing applications that use %{name}.


%prep
%autosetup -c -p1
%if %{with python}
# this file gets cached starting in 841d5087eda926eac1cb17c4683fd48b247afe50
# but it depends on executor_api.h which is generated alongside executor.cpp
# delete this file so we regenerate both and allow the Python extension to be built
rm folly/python/executor.cpp
%endif


%build
# static build
mkdir %{_static_builddir}
pushd %{_static_builddir}
# let's build tests only in the static build since that's what upstream recommends anyway
%if %{with tests}
%cmake .. \
  -DBUILD_TESTS=ON \
%else
%cmake .. \
%endif
  -DBUILD_SHARED_LIBS=OFF \
  -DCMAKE_INSTALL_DIR=%{_libdir}/cmake/%{name}-static \
  -DPACKAGE_VERSION=%{version} \
  -DPYTHON_EXTENSIONS=OFF
%cmake_build
popd

%cmake \
  -DBUILD_SHARED_LIBS=ON \
%if %{with python}
  -DPYTHON_EXTENSIONS=ON \
%endif
  -DCMAKE_INSTALL_DIR=%{_libdir}/cmake/%{name} \
  -DPACKAGE_VERSION=%{version}
%cmake_build

# Build documentation
make -C folly/docs


%install
# static build
pushd %{_static_builddir}
%cmake_install
popd

# shared build
%cmake_install

%if %{with python}
# these should not be packaged
rm %{buildroot}/%{python3_sitearch}/%{name}/*.{h,pxd}
%endif

find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'


%if %{with tests}
%check
pushd %{_static_builddir}
%ctest
popd
%endif


%files
%license LICENSE
%{_libdir}/*.so.*

%files devel
%doc CODE_OF_CONDUCT.md CONTRIBUTING.md README.md
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/cmake/%{name}
%{_libdir}/pkgconfig/lib%{name}.pc

%files docs
%doc folly/docs/*.html

%if %{with python}
%files -n python3-%{name}
%{python3_sitearch}/%{name}
%{python3_sitearch}/%{name}-0.0.1-py%{python3_version}.egg-info
%endif

%files static
%{_libdir}/*.a
%{_libdir}/cmake/%{name}-static


%changelog
* Fri Nov  6 2020 Michel Alexandre Salim <salimma@fedoraproject.org> - 2020.11.02.00-2
- Enable Python bindings by default

* Mon Nov  2 2020 Michel Alexandre Salim <salimma@fedoraproject.org> - 2020.11.02.00-1
- Update to 2020.11.02.00

* Mon Oct 26 2020 Michel Alexandre Salim <salimma@fedoraproject.org> - 2020.10.26.00-1
- Update to 2020.10.26.00
- Build docs
- Don't run tests if built without tests

* Thu Oct 22 2020 Michel Alexandre Salim <salimma@fedoraproject.org> - 2020.10.19.00-4
- Put static cmake support files in its own directory
- Add most folly BRs as folly-devel requirements, as dependent packages will need them

* Wed Oct 21 2020 Michel Alexandre Salim <salimma@fedoraproject.org> - 2020.10.19.00-3
- Provide both shared and static libraries

* Tue Oct 20 2020 Michel Alexandre Salim <salimma@fedoraproject.org> - 2020.10.19.00-2
- Add libiberty and zstd BRs
- Try compiling Python extensions

* Tue Oct 20 2020 Michel Alexandre Salim <salimma@fedoraproject.org> - 2020.10.19.00-1
- Update to 2020.10.19.00
- Fix compile error on i686
- Fix compile error on armv7hl (requires liburing >= 0.7-3)
- Exclude s390x

* Mon Oct 12 14:54:12 PDT 2020 Michel Alexandre Salim <salimma@fedoraproject.org> - 2020.10.12.00-1
- Initial package
