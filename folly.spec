%if 0%{?fedora} >= 36
# FTBFS with GCC 12
%bcond_without toolchain_clang
%else
%bcond_with toolchain_clang
%endif

%if %{with toolchain_clang}
%global toolchain clang
%ifarch %{ix86} x86_64
# tests can be compiled, keep it that way
%bcond_without check
%else
# tests don't compile cleanly on aarch64 and ppc64le yet
%bcond_with check
%endif
%else
# GCC: some tests fail to compile
%bcond_with check
%endif

%if 0%{?el9}
# pandoc is not in CS9
# https://bugzilla.redhat.com/show_bug.cgi?id=2035151
%bcond_with docs
%else
%bcond_without docs
%endif

%bcond_without python

Name:           folly
Version:        2022.02.28.00
Release:        %{autorelease}
Summary:        An open-source C++ library developed and used at Facebook

License:        ASL 2.0
URL:            https://github.com/facebook/folly
Source:         %{url}/archive/v%{version}/folly-%{version}.tar.gz
Patch0:         %{name}-badge_revert_for_gcc11.patch
Patch1:         %{name}-fix_sslerrors_test_for_v3.patch
Patch2:         %{name}-fix_codel_test.patch
Patch3:         %{name}-fix_async_udp_socket_integration_test.patch
Patch4:         %{name}-skip_packed_sync_ptr_test_32bit.patch
Patch5:         %{name}-skip_bitvectorcoding_test_non_x64.patch
Patch6:         %{name}-skip_eliasfanocoding_test_non_x64.patch
Patch7:         %{name}-fix_bits_test_32bit.patch
Patch8:         %{name}-fix_small_locks_test.patch
Patch9:         %{name}-skip_discriminatedptr_test_32bit.patch
# /builddir/build/BUILD/folly-2022.02.28.00/folly/experimental/exception_tracer/ExceptionTracer.cpp:131:10: error: no matching function for call to 'isAbiCppException'
#   return isAbiCppException(tag{}, exc->unwindHeader.exception_class);
#          ^~~~~~~~~~~~~~~~~
# /builddir/build/BUILD/folly-2022.02.28.00/folly/experimental/exception_tracer/ExceptionTracer.cpp:117:25: note: candidate function not viable: no known conversion from 'const uint64_t' (aka 'const unsigned long long') to 'const char [8]' for 2nd argument
# FOLLY_MAYBE_UNUSED bool isAbiCppException(ArmAbiTag, const char (&klazz)[8]) {
#                         ^
# /builddir/build/BUILD/folly-2022.02.28.00/folly/experimental/exception_tracer/ExceptionTracer.cpp:122:25: note: candidate function not viable: no known conversion from 'tag' (aka 'folly::exception_tracer::(anonymous namespace)::ArmAbiTag') to 'folly::exception_tracer::(anonymous namespace)::AnyAbiTag' for 1st argument
# FOLLY_MAYBE_UNUSED bool isAbiCppException(AnyAbiTag, const uint64_t& klazz) {
#                         ^
# /builddir/build/BUILD/folly-2022.02.28.00/folly/experimental/exception_tracer/ExceptionTracer.cpp:129:6: note: candidate function not viable: requires single argument 'exc', but 2 arguments were provided
# bool isAbiCppException(const __cxa_exception* exc) {
#      ^
Patch11:        %{name}-disable_exception_tracer_armv7hl.patch

# Folly is known not to work on big-endian CPUs
# https://bugzilla.redhat.com/show_bug.cgi?id=1892151
ExcludeArch:    s390x
%if 0%{?fedora} > 36
# fmt code breaks: https://bugzilla.redhat.com/show_bug.cgi?id=2061022
# /usr/bin/ld: ../../../libfolly.so.2022.02.28.00: undefined reference to `int fmt::v8::detail::format_float<__float128>(__float128, int, fmt::v8::detail::float_specs, fmt::v8::detail::buffer<char>&)'
# /usr/bin/ld: ../../../libfolly.so.2022.02.28.00: undefined reference to `int fmt::v8::detail::snprintf_float<__float128>(__float128, int, fmt::v8::detail::float_specs, fmt::v8::detail::buffer<char>&)'
ExcludeArch:    ppc64le
%endif

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
# 0.7-3 fixes build on armv7hl
BuildRequires:  liburing-devel >= 0.7-3
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
Requires:       liburing-devel%{?_isa} >= 0.7-3
Requires:       libzstd-devel%{?_isa}
Requires:       lz4-devel%{?_isa}
Requires:       openssl-devel%{?_isa}
Requires:       snappy-devel%{?_isa}
Requires:       xz-devel%{?_isa}
Requires:       zlib-devel%{?_isa}
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
%setup -q
%if %{without toolchain_clang} && ! 0%{?el8}
# el9 and fedora have GCC >= 11
%patch0 -p1
%endif
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%ifarch ppc64le
%patch10 -p1
%endif
%ifarch armv7hl
%patch11 -p1
rm -rf folly/experimental/exception_tracer
%endif

%if %{with python}
# this file gets cached starting in 841d5087eda926eac1cb17c4683fd48b247afe50
# but it depends on executor_api.h which is generated alongside executor.cpp
# delete this file so we regenerate both and allow the Python extension to be built
rm folly/python/executor.cpp
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
# x86_64: disable flaky tests
# ix86: some tests are still failing
%{__ctest} --output-on-failure --force-new-ctest-process %{?_smp_mflags} \
%ifarch x86_64
  -E 'fbstring_test\.FBString\.testAllClauses' \
  -E 'glog_test\.LogEveryMs\.basic'
%else
%ifarch %{ix86}
  -E 'cache_locality_test\.CoreRawAllocator\.Basic' \
  -E 'chrono_conv_test\.Conv' \
  -E 'cpu_id_test\.CpuId\.Simple' \
  -E 'event_count_test\.EventCount\.Simple' \
  -E 'f14_map_test\.F14Map\.continuousCapacitySmall0' \
  -E 'fbstring_test\.' \
  -E 'memcpy_test\.folly_memcpy\.overlap' \
  -E 'memory_test\.' \
  -E 'thread_cached_int_test\.ThreadCachedIntTest\.MultithreadedFast' \
  -E 'threaded_executor_test\.ThreadedExecutorTest\.many'
%endif
%endif

cd -
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
