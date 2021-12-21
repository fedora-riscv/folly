%bcond_without python

%if 0%{?el9}
%bcond_with dwarf
%else
%bcond_without dwarf
%endif

# No tests were found:
# https://github.com/facebook/folly/issues/1671
%bcond_with tests

%global _static_builddir static_build

Name:           folly
Version:        2021.11.29.00
Release:        %{autorelease}
Summary:        An open-source C++ library developed and used at Facebook

License:        ASL 2.0
URL:            https://github.com/facebook/folly
Source0:        %{url}/archive/v%{version}/folly-%{version}.tar.gz
Patch0:         %{name}-drop-immintrin.patch
Patch1:         %{name}-gcc-enable-coroutines.patch

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
BuildRequires:  gtest-devel
%endif
BuildRequires:  libaio-devel
%if %{with dwarf}
BuildRequires:  libdwarf-devel
%endif
BuildRequires:  libevent-devel
BuildRequires:  libsodium-devel
BuildRequires:  libunwind-devel
# 0.7-3 fixes build on armv7hl
BuildRequires:  liburing-devel >= 0.7-3
BuildRequires:  libzstd-devel
BuildRequires:  lz4-devel
BuildRequires:  openssl-devel
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
BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(cython)
BuildRequires:  python3dist(wheel)
BuildRequires: make
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n python3-%{name}
The python3-%{name} package contains Python bindings for %{name}.


%package -n python3-%{name}-devel
Summary:        Development files for python3-%{name}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Requires:       python3-%{name}%{?_isa} = %{version}-%{release}

%description -n python3-%{name}-devel
The python3-%{name}-devel package contains libraries and header files for
developing applications that use python3-%{name}.
%endif


%package        static
Summary:        Static development libraries for %{name}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}

%description    static
The %{name}-static package contains static libraries for
developing applications that use %{name}.


%prep
%autosetup -p1
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
%cmake .. \
%if %{with tests}
  -DBUILD_TESTS=ON \
%endif
  -DBUILD_SHARED_LIBS=OFF \
  -DCMAKE_INSTALL_DIR=%{_libdir}/cmake/%{name}-static \
%if %{with dwarf} && 0%{?fedora}
  -DLIBDWARF_INCLUDE_DIR=%{_includedir}/libdwarf-0 \
%endif
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
%if %{with tests} && 0%{?fedora}
  -DLIBDWARF_INCLUDE_DIR=%{_includedir}/libdwarf-0 \
%endif
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
%exclude %{_includedir}/folly/python

%files docs
%doc folly/docs/*.html

%if %{with python}
%files -n python3-%{name}
%{python3_sitearch}/%{name}
%{python3_sitearch}/%{name}-0.0.1-py%{python3_version}.egg-info
%exclude %{python3_sitearch}/%{name}/*.h
%exclude %{python3_sitearch}/%{name}/*.pxd

%files -n python3-%{name}-devel
%{_includedir}/folly/python
%{python3_sitearch}/%{name}/*.h
%{python3_sitearch}/%{name}/*.pxd
%endif

%files static
%{_libdir}/*.a
%{_libdir}/cmake/%{name}-static


%changelog
%autochangelog
