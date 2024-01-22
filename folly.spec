%bcond_with toolchain_clang

%if %{with toolchain_clang}
%global toolchain clang
%endif
%ifarch x86_64 aarch64
# tests can be compiled, keep it that way
# on aarch64 ctest doesn't seem to find tests yet
%bcond_without check
%else
# tests don't compile cleanly on ppc64le yet
%bcond_with check
%endif

# use this to re-test running all tests
%bcond_with all_tests

%ifarch aarch64
# In file included from /builddir/build/BUILD/folly-2023.04.24.00/folly/detail/SplitStringSimd.cpp:18:
# /builddir/build/BUILD/folly-2023.04.24.00/folly/detail/SplitStringSimdImpl.h: In static member function 'static uint64_t folly::detail::StringSplitAarch64Platform::equal(reg_t, char)':
# /builddir/build/BUILD/folly-2023.04.24.00/folly/detail/SplitStringSimdImpl.h:129:25: note: use '-flax-vector-conversions' to permit conversions between vectors with differing element types or numbers of subparts
#   129 |     return vget_lane_u64(vmovn_u16(u16s), 0);
#       |            ~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~
# /builddir/build/BUILD/folly-2023.04.24.00/folly/detail/SplitStringSimdImpl.h:129:35: error: cannot convert 'uint8x8_t' to 'uint64x1_t'
#   129 |     return vget_lane_u64(vmovn_u16(u16s), 0);
#       |                          ~~~~~~~~~^~~~~~
#       |                                   |
#       |                                   uint8x8_t
# In file included from /builddir/build/BUILD/folly-2023.04.24.00/folly/detail/SplitStringSimdImpl.h:29:
# /usr/lib/gcc/aarch64-redhat-linux/13/include/arm_neon.h:2725:27: note:   initializing argument 1 of 'uint64_t vget_lane_u64(uint64x1_t, int)'
#  2725 | vget_lane_u64 (uint64x1_t __a, const int __b)
#       |                ~~~~~~~~~~~^~~
%global optflags %optflags -flax-vector-conversions
%endif

%if 0%{?el9}
# pandoc is not in CS9
# https://bugzilla.redhat.com/show_bug.cgi?id=2035151
%bcond_with docs
%else
%bcond_without docs
%endif

# Python bindings not buildable with CMake
# folly/iobuf.cpp:20:10: fatal error: folly/python/iobuf_api.h: No such file or directory   
%bcond_with python

%global liburing_min_version 2.1
%if 0%{?fedora} || 0%{?rhel} >= 10
%bcond_without uring
%else
# liburing too old: IORING_CQE_F_MORE added in
# 674d092f634e61ab1ec72c190a29bc9bde0f5076 included in 2.1+
%bcond_with uring
%endif

Name:           folly
Version:        2024.01.22.00
Release:        %{autorelease}
Summary:        An open-source C++ library developed and used at Facebook

License:        Apache-2.0
URL:            https://github.com/facebook/folly
Source:         %{url}/archive/v%{version}/folly-%{version}.tar.gz
# workaround in https://github.com/facebook/folly/issues/1991 no longer works with GCC 14.0.1
# https://github.com/facebook/folly/issues/2129
Patch:          folly-gcc14-fix-type-pack-element-again.diff
# need to include algorithm header for std::count_if. Being upstreamed.
Patch:          folly-gcc14-add-algorithm-for-count_if.diff

ExclusiveArch:  x86_64 aarch64 ppc64le

BuildRequires:  cmake
%if %{with toolchain_clang}
BuildRequires:  clang
BuildRequires:  libatomic
%else
BuildRequires:  gcc-c++
%endif
# Docs dependencies
%if %{with docs}
BuildRequires:  pandoc
%endif
# Library dependencies
# for libiberty
BuildRequires:  binutils-devel
BuildRequires:  boost-devel
BuildRequires:  bzip2-devel
BuildRequires:  double-conversion-devel
BuildRequires:  fmt-devel
BuildRequires:  gflags-devel
BuildRequires:  glog-devel
%if %{with check}
BuildRequires:  gmock-devel
BuildRequires:  gtest-devel
%endif
BuildRequires:  libaio-devel
BuildRequires:  libdwarf-devel
BuildRequires:  libevent-devel
BuildRequires:  libsodium-devel
BuildRequires:  libunwind-devel
%if %{with uring}
# 0.7-3 fixes build on armv7hl
BuildRequires:  liburing-devel >= %{liburing_min_version}
%endif
BuildRequires:  libzstd-devel
BuildRequires:  lz4-devel
BuildRequires:  openssl-devel
BuildRequires:  snappy-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel

%global _description %{expand:
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
Folly.}

%description %{_description}


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
%if %{with uring}
Requires:       liburing-devel%{?_isa} >= %{liburing_min_version}
%endif
Requires:       libzstd-devel%{?_isa}
Requires:       lz4-devel%{?_isa}
Requires:       openssl-devel%{?_isa}
Requires:       snappy-devel%{?_isa}
Requires:       xz-devel%{?_isa}
Requires:       zlib-devel%{?_isa}
%if %{without python}
Obsoletes:      python3-%{name} < 2023.04.24.00-1
%endif
Obsoletes:      %{name}-static < 2022.02.28.00-1

%description    devel %{_description}

The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%if %{with docs}
%package        docs
Summary:        Documentation for %{name}
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}

%description    docs %{_description}

The %{name}-docs package contains documentation for %{name}.
%endif


%if %{with python}
%package -n python3-%{name}
Summary:        Python bindings for %{name}
BuildRequires:  make
BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(cython)
BuildRequires:  python3dist(wheel)
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n python3-%{name} %{_description}

The python3-%{name} package contains Python bindings for %{name}.


%package -n python3-%{name}-devel
Summary:        Development files for python3-%{name}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Requires:       python3-%{name}%{?_isa} = %{version}-%{release}

%description -n python3-%{name}-devel %{_description}

The python3-%{name}-devel package contains libraries and header files for
developing applications that use python3-%{name}.
%endif


%prep
%autosetup -p1

%if %{with python}
# this file gets cached starting in 841d5087eda926eac1cb17c4683fd48b247afe50
# but it depends on executor_api.h which is generated alongside executor.cpp
# delete this file so we regenerate both and allow the Python extension to be built
rm folly/python/executor.cpp
%endif

%if %{with toolchain_clang}
%ifarch ppc64le
# folly/logging/example/logging_example: link failure wrt fmt
sed -i folly/CMakeLists.txt -e '\@logging/example@s|add_subdirectory|#add_subdirectory|'
%endif
%endif

%build
%cmake \
  -DBUILD_SHARED_LIBS=ON \
%if %{with python}
  -DPYTHON_EXTENSIONS=ON \
%endif
%if %{with check}
  -DBUILD_TESTS=ON \
%endif
  -DCMAKE_INSTALL_DIR=%{_libdir}/cmake/%{name} \
%if 0%{?fedora} >= 36 || 0%{?rhel} >= 9
  -DLIBDWARF_INCLUDE_DIR=%{_includedir}/libdwarf-0 \
%endif
  -DPACKAGE_VERSION=%{version}
%cmake_build

%if %{with docs}
# Build documentation
make -C folly/docs
%endif


%install
%cmake_install


%if %{with check}
%check
%if %{with all_tests}
%ctest
%else
# x86_64: disable flaky tests
# ix86: some tests are still failing
cd "%{__cmake_builddir}"

# flaky tests
EXCLUDED_TESTS='-E DISABLED'
EXCLUDED_TESTS+='|glog_test\.LogEveryMs\.basic'
EXCLUDED_TESTS+='|fbstring_test\.FBString\.testAllClauses'
EXCLUDED_TESTS+='|AsyncUDPSocketTest\.AsyncSocketIntegrationTest\.PingPongNotifyMmsg'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.CancelTimeout'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.ReschedTest'
EXCLUDED_TESTS+='|fbvector_test\.'

%ifarch aarch64
EXCLUDED_TESTS+='|cache_locality_test\.Getcpu\.VdsoGetcpu'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.FireOnce'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.DestroyTimeoutSet'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.SlowFast'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.DefaultTimeout'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.IntrusivePtr'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.GetTimeRemaining'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.Level1'
EXCLUDED_TESTS+='|timeseries_histogram_test\.TimeseriesHistogram\.Percentile'
EXCLUDED_TESTS+='|memcpy_test\.folly_memcpy\.overlap'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.DeleteWheelInTimeout'
EXCLUDED_TESTS+='|HHWheelTimerTest\.HHWheelTimerTest\.NegativeTimeout'
EXCLUDED_TESTS+='|cache_locality_test\.CacheLocality\.LinuxActual'
EXCLUDED_TESTS+='|small_locks_test\.SmallLocks\.SpinLockCorrectness'
EXCLUDED_TESTS+='|locks_test\.SpinLock\.Correctness'
EXCLUDED_TESTS+='|fbstring_test\.FBString\.testAllClauses'
%endif

%{__ctest} --output-on-failure --force-new-ctest-process %{?_smp_mflags} \
  ${EXCLUDED_TESTS}

cd -
%endif
%endif


%files
%license LICENSE
%{_libdir}/*.so.%{version}

%files devel
%doc CODE_OF_CONDUCT.md CONTRIBUTING.md README.md
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/cmake/%{name}
%{_libdir}/pkgconfig/lib%{name}.pc
%exclude %{_includedir}/folly/python

%if %{with docs}
%files docs
%doc folly/docs/*.html
%endif

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


%changelog
%autochangelog
