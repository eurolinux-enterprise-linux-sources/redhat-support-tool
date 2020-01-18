#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

%global         package_version 0.9.6-0
%global         package_name redhat-support-tool

Name:           %{package_name}
Version:        0.9.6
Release:        0%{?release_suffix}%{?dist}
Summary:        Tool for console access to Red Hat subscriber services
Vendor:         Red Hat, Inc.
Group:          Development/Libraries
License:        ASL 2.0
URL:            https://api.access.redhat.com
Source0:        http://people.redhat.com/kroberts/projects/redhat-support-tool/%{package_name}-%{package_version}.tar.gz

BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildArch: noarch
%{!?dist:BuildRequires: buildsys-macros}

Requires: python
Requires: python-lxml
Requires: python-dateutil
Requires: redhat-support-lib-python >= 0.9.6-0

%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
BuildRoot: %{_topdir}/BUILDROOT/%{name}-%{version}-%{release}.%{_arch}
%endif

%description
This package contains the Red Hat Support Tool.  The Red Hat Support Tool
provides console based access to Red Hat's subscriber services.  These
services include, but are not limited to, console based access to
knowledge-base solutions, case management, automated diagnostic
services, etc.

%prep
%setup -q -n %{package_name}-%{package_version}

%build
%configure \
        --disable-python-syntax-check

make %{?_smp_mflags}

# For sample vendor plugin
mkdir -p samples/vendors/
mv src/redhat_support_tool/vendors/ACMECorp samples/vendors/

%install
rm -rf "%{buildroot}"
make %{?_smp_mflags} install DESTDIR="%{buildroot}"

%if 0%{?rhel} && 0%{?rhel} <= 5
%clean
rm -rf "%{buildroot}"
%endif

%files
%doc AUTHORS README README.plugins samples/
%{python_sitelib}/redhat_support_tool/
%{_bindir}/redhat-support-tool

%changelog
* Wed Feb 26 2014 Keith Robertson <kroberts@redhat.com> - 0.9.6-0
- Resolves: rhbz#983968
- Resolves: rhbz#1036707
- Resolves: rhbz#1036713
- Resolves: rhbz#1036783
- Resolves: rhbz#1037647

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.9.5-9
- Mass rebuild 2013-12-27

* Mon Aug 12 2013 Keith Robertson <kroberts@redhat.com> - 0.9.5-8
- Resolves: rhbz#983909

* Wed Jul 24 2013 Keith Robertson <kroberts@redhat.com> - 0.9.5-6
- Resolves: rhbz#983903
- Resolves: rhbz#983896

* Mon Jul 22 2013 Keith Robertson <kroberts@redhat.com> - 0.9.5-4
- Various issues with btextract

* Tue Jun 11 2013 Keith Robertson <kroberts@redhat.com> - 0.9.5-3
- Resolves: rhbz#880777

* Tue Jun 11 2013 Keith Robertson <kroberts@redhat.com> - 0.9.5-2
- Various updates including;
  - Filtering and pagination of listcases
  - casegroup command
  - opencase is in the analyze and diagnose commands
  
* Thu May 23 2013 Nigel Jones <nigjones@redhat.com> - 0.9.4-1
- Diagnostics:
  - Opening a case will now trigger the case recommendations engine
    prior to opening the case.
  - Extracted backtraces from kernel vmcores can be passed to
    Ask Shadowman at the users request
- Case Handling:
  - modifycase can be triggered on a selected case
  - Per above, opencase/diagnostics support
- Plugins:
  - Ability for Vendor/L3 plugins
  - Sample 'ACMECorp' plugin + README.plugins in documentation directory.
- Localization/Internationalization:
  - Changes to support non-ASCII character input from character sets used in
    Red Hat GSS supported languages.

* Wed May 1 2013 Nigel Jones <nigjones@redhat.com> - 0.9.3-1
- Pagination bug fix to fix an offsetting bug that could contribute
  to missing, or duplicate results.

* Fri Apr 26 2013 Nigel Jones <nigjones@redhat.com> - 0.9.2-1
- Various updates to source, including:
  - Pagination of 'listcases'
  - Better debugability
  - Splitfile abilities to 'addattachment'
  - Recommendations support
  - Changes to 'downloadall' attachment handling

* Wed Feb 20 2013 Nigel Jones <nigjones@redhat.com> - 0.9.0-2
- Import into Red Hat packaging system

* Fri Apr 13 2012 Keith Robertson <kroberts@redhat.com> - 0.9.0-1
- Initial build
