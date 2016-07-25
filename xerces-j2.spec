%global pkg_name xerces-j2
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

%global cvs_version 2_11_0

%define __requires_exclude system.bundle

Name:          %{?scl_prefix}%{pkg_name}
Version:       2.11.0
Release:       17.1%{?dist}
Summary:       Java XML parser
License:       ASL 2.0
URL:           http://xerces.apache.org/xerces2-j/

Source0:       http://mirror.ox.ac.uk/sites/rsync.apache.org/xerces/j/source/Xerces-J-src.%{version}.tar.gz
Source1:       %{pkg_name}-version.sh
Source2:       %{pkg_name}-constants.sh
Source11:      %{pkg_name}-version.1
Source12:      %{pkg_name}-constants.1

# Custom javac ant task used by the build
Source3:       https://svn.apache.org/repos/asf/xerces/java/tags/Xerces-J_%{cvs_version}/tools/src/XJavac.java

# Custom doclet tags used in javadocs
Source5:       https://svn.apache.org/repos/asf/xerces/java/tags/Xerces-J_%{cvs_version}/tools/src/ExperimentalTaglet.java
Source6:       https://svn.apache.org/repos/asf/xerces/java/tags/Xerces-J_%{cvs_version}/tools/src/InternalTaglet.java

Source7:       %{pkg_name}-pom.xml

# Patch the build so that it doesn't try to use bundled xml-commons source
Patch0:        %{pkg_name}-build.patch

# Patch the manifest so that it includes OSGi stuff
Patch1:        %{pkg_name}-manifest.patch

# Fix XML parsing bug (JAXP, 8017298)
# Backported from upstream commit http://svn.apache.org/viewvc?view=revision&revision=1499506
Patch2:        %{pkg_name}-CVE-2013-4002.patch

BuildArch:     noarch

BuildRequires: %{?scl_prefix}javapackages-tools
BuildRequires: %{?scl_prefix}xalan-j2 >= 2.7.1
BuildRequires: %{?scl_prefix}xml-commons-apis >= 1.4.01
BuildRequires: %{?scl_prefix}xml-commons-resolver >= 1.2
BuildRequires: %{?scl_prefix}ant
BuildRequires: %{?scl_prefix}xerces-j2
BuildRequires: dejavu-sans-fonts
Requires:      %{?scl_prefix}xalan-j2 >= 2.7.1
Requires:      %{?scl_prefix}xml-commons-apis >= 1.4.01
Requires:      %{?scl_prefix}xml-commons-resolver >= 1.2

# This documentation is provided by xml-commons-apis

# http://mail-archives.apache.org/mod_mbox/xerces-j-dev/201008.mbox/%3COF8D7E2F83.0271A181-ON8525777F.00528302-8525777F.0054BBE0@ca.ibm.com%3E

%description
Welcome to the future! Xerces2 is the next generation of high performance,
fully compliant XML parsers in the Apache Xerces family. This new version of
Xerces introduces the Xerces Native Interface (XNI), a complete framework for
building parser components and configurations that is extremely modular and
easy to program.

The Apache Xerces2 parser is the reference implementation of XNI but other
parser components, configurations, and parsers can be written using the Xerces
Native Interface. For complete design and implementation documents, refer to
the XNI Manual.

Xerces2 is a fully conforming XML Schema processor. For more information,
refer to the XML Schema page.

Xerces2 also provides a complete implementation of the Document Object Model
Level 3 Core and Load/Save W3C Recommendations and provides a complete
implementation of the XML Inclusions (XInclude) W3C Recommendation. It also
provides support for OASIS XML Catalogs v1.1.

Xerces2 is able to parse documents written according to the XML 1.1
Recommendation, except that it does not yet provide an option to enable
normalization checking as described in section 2.13 of this specification. It
also handles name spaces according to the XML Namespaces 1.1 Recommendation,
and will correctly serialize XML 1.1 documents if the DOM level 3 load/save
APIs are in use.

%package        javadoc
Summary:        Javadocs for %{pkg_name}

# Consolidating all javadocs into one package

%description    javadoc
This package contains the API documentation for %{pkg_name}.

%package        demo
Summary:        Demonstrations and samples for %{pkg_name}
Requires:       %{name} = %{version}-%{release}

%description    demo
%{summary}.

%prep
%setup -q -n xerces-%{cvs_version}
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%patch0 -p0 -b .orig
%patch1 -p0 -b .orig
%patch2 -p0 -b .orig

# Copy the custom ant tasks into place
mkdir -p tools/org/apache/xerces/util
mkdir -p tools/bin
cp -a %{SOURCE3} %{SOURCE5} %{SOURCE6} tools/org/apache/xerces/util

# Make sure upstream hasn't sneaked in any jars we don't know about
find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;

sed -i 's/\r//' LICENSE README NOTICE
%{?scl:EOF}

%build
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
pushd tools

# Build custom ant tasks
javac -classpath $(build-classpath ant) org/apache/xerces/util/XJavac.java
jar cf bin/xjavac.jar org/apache/xerces/util/XJavac.class

# Build custom doc taglets
javac -classpath /usr/lib/jvm/java/lib/tools.jar org/apache/xerces/util/*Taglet.java
jar cf bin/xerces2taglets.jar org/apache/xerces/util/*Taglet.class

ln -sf $(build-classpath xalan-j2) serializer.jar
ln -sf $(build-classpath xml-commons-apis) xml-apis.jar
ln -sf $(build-classpath xml-commons-resolver) resolver.jar
popd

# Build everything
export ANT_OPTS="-Xmx256m -Djava.endorsed.dirs=$(pwd)/tools -Djava.awt.headless=true -Dbuild.sysclasspath=first -Ddisconnected=true"
ant -Djavac.source=1.5 -Djavac.target=1.5 \
    -Dbuild.compiler=modern \
    clean jars javadocs
%{?scl:EOF}

%install
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
# jars
install -pD -T build/xercesImpl.jar %{buildroot}%{_javadir}/%{pkg_name}.jar

# javadoc
mkdir -p %{buildroot}%{_javadocdir}/%{pkg_name}
mkdir -p %{buildroot}%{_javadocdir}/%{pkg_name}/impl
mkdir -p %{buildroot}%{_javadocdir}/%{pkg_name}/xs
mkdir -p %{buildroot}%{_javadocdir}/%{pkg_name}/xni
mkdir -p %{buildroot}%{_javadocdir}/%{pkg_name}/other

cp -pr build/docs/javadocs/xerces2/* %{buildroot}%{_javadocdir}/%{pkg_name}/impl
cp -pr build/docs/javadocs/api/* %{buildroot}%{_javadocdir}/%{pkg_name}/xs
cp -pr build/docs/javadocs/xni/* %{buildroot}%{_javadocdir}/%{pkg_name}/xni
cp -pr build/docs/javadocs/other/* %{buildroot}%{_javadocdir}/%{pkg_name}/other

# scripts
install -pD -m755 -T %{SOURCE1} %{buildroot}%{_bindir}/%{pkg_name}-version
install -pD -m755 -T %{SOURCE2} %{buildroot}%{_bindir}/%{pkg_name}-constants

# manual pages
install -d -m 755 %{buildroot}%{_mandir}/man1
install -p -m 644 %{SOURCE11} %{buildroot}%{_mandir}/man1
install -p -m 644 %{SOURCE12} %{buildroot}%{_mandir}/man1

# demo
install -pD -T build/xercesSamples.jar %{buildroot}%{_datadir}/%{pkg_name}/%{pkg_name}-samples.jar
cp -pr data %{buildroot}%{_datadir}/%{pkg_name}

# Pom
install -pD -T -m 644 %{SOURCE7} %{buildroot}%{_mavenpomdir}/JPP-%{pkg_name}.pom

# Depmap with legacy depmaps for compatability
%add_maven_depmap JPP-%{pkg_name}.pom %{pkg_name}.jar -a "xerces:xerces" -a "xerces:xmlParserAPIs"
%{?scl:EOF}

%files
%doc LICENSE NOTICE README
%{_mavendepmapfragdir}/*
%{_mavenpomdir}/*
%{_javadir}/%{pkg_name}*
%{_bindir}/*
%{_mandir}/*/*

%files javadoc
%dir %{_javadocdir}/%{pkg_name}
%{_javadocdir}/%{pkg_name}/impl
%{_javadocdir}/%{pkg_name}/xs
%{_javadocdir}/%{pkg_name}/xni
%{_javadocdir}/%{pkg_name}/other

%files demo
%defattr(-,root,root,-)
%{_datadir}/%{pkg_name}

%changelog
* Thu Sep 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-17.1
- Fix XML parsing bug (JAXP, 8017298)
- Resolves: CVE-2013-4002

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-16.10
- Mass rebuild 2014-05-26

* Thu Feb 20 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-16.9
- Fix unowned directory

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-16.8
- Mass rebuild 2014-02-19

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-16.7
- Mass rebuild 2014-02-18

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-16.6
- Remove requires on java

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-16.5
- Don't install jaxp_parser_impl provider for alternatives

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-16.4
- SCL-ize build-requires

* Fri Feb 14 2014 Michael Simacek <msimacek@redhat.com> - 2.11.0-16.3
- SCL-ize BR

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-16.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-16.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 2.11.0-16
- Mass rebuild 2013-12-27

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-15
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Mon May 20 2013 Krzysztof Daniel <kdaniel@redhat.com> 2.11.0-13
- Add reexoport to javax.xml.

* Mon Apr  8 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.11.0-13
- Add manual pages

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.11.0-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Dec 17 2012 Alexander Kurtakov <akurtako@redhat.com> 2.11.0-11
- Really restore dependencies.

* Tue Dec 11 2012 Krzysztof Daniel <kdaniel@redhat.com> 2.11.0-10
- Restored dependencies to system.bundle and javax.xml.

* Tue Sep 25 2012 Krzysztof Daniel <kdaniel@redhat.com> 2.11.0-9
- Remove javax.xml from required bundles. They are provided by JVM.

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.11.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Apr 18 2012 Krzysztof Daniel <kdaniel@redhat.com> 2.11.0-7
- Updated OSGi MANIFEST.MF to import javax.xml

* Thu Mar 08 2012 Andrew Overholt <overholt@redhat.com> - 2.11.0-6
- Remove system.bundle OSGi requirement from MANIFEST.MF
- Fold -scripts sub-package into main

* Tue Mar 06 2012 Marek Goldmann <mgoldman@redhat.com> - 2.11.0-5
- Use non-versioned jar name, RHBZ#800463
- Cleanup in spec file to follow new guidelines
- Consolidated javadocs packages
- Removed manual subpackage because of stylebook issues, see comment on obsolete

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.11.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.11.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Dec 13 2010 Mat Booth <fedora@matbooth.co.uk> 2.11.0-2
- Install maven pom and depmap.

* Sat Dec 11 2010 Mat Booth <fedora@matbooth.co.uk> - 2.11.0-1
- Update to latest upstream version.
- Provide JAXP 1.4.
- Fix some minor rpmlint warnings.
- Add dep on xalan-j2.
- Fix javadoc taglets.

* Sat Jun 12 2010 Mat Booth <fedora@matbooth.co.uk> - 2.9.0-4
- Fix broken links in manual and fix javadoc requires.
- Build 1.5 bytecode instead of 1.6, for compatibility.

* Fri Jan 22 2010 Andrew Overholt <overholt@redhat.com> - 2.9.0-3
- Fix unversioned Provides for jaxp_parser_impl (make it 1.3).

* Thu Jan 14 2010 Mat Booth <fedora@matbooth.co.uk> - 2.9.0-2
- Add a build dep on a font package because the JDK is missing a dependency
  to function correctly in headless mode. See RHBZ #478480 and #521523.
- Fix groups.

* Tue Jan 5 2010 Mat Booth <fedora@matbooth.co.uk> - 2.9.0-1
- Update to 2.9.0: This is the version Eclipse expects, previously the OSGi
  manifest was lying about its version :-o
- Enable manual sub-package now xml-stylebook is in Fedora.
- Drop GCJ support.
- Minor changes to spec to make it more conforming to the guidelines.
- Drop the libgcj patch, we don't seem to need it anymore.
- Add the OSGi manifest as part of the build instead of the install.
- Fix packaging bug RHBZ #472646.

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.1-12.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.1-11.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan 30 2009 Alexander Kurtakov <akurtako@redhat.com> 0:2.7.1-10.3
- Add osgi manifest.

* Thu Jul 10 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:2.7.1-10.2
- drop repotag
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:2.7.1-10jpp.1
- Autorebuild for GCC 4.3

* Wed Mar 28 2007 Matt Wringe <mwringe@redhat.com> 0:2.7.1-9jpp.1
- Update with newest jpp version
- Clean up spec file for Fedora Review

* Sun Aug 13 2006 Warren Togami <wtogami@redhat.com> 0:2.7.1-7jpp.2
- fix typo in preun req

* Sat Aug 12 2006 Matt Wringe <mwringe at redhat.com> 0:2.7.1-7jpp.1
- Merge with upstream version

* Sat Aug 12 2006 Matt Wringe <mwringe at redhat.com> 0:2.7.1-7jpp
- Add conditional native compiling
- Add missing requires for javadocs
- Add missing requires for post and preun
- Update version to 7jpp at Fedora's request

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:2.7.1-6jpp_9fc
- Rebuilt

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0:2.7.1-6jpp_8fc
- rebuild

* Thu Mar 30 2006 Fernando Nasser <fnasser@redhat.com> 0:2.7.1-3jpp
- Add missing BR for xml-stylebook

* Wed Mar 22 2006 Ralph Apel <r.apel at r-apel.de> 0:2.7.1-2jpp
- First JPP-1.7 release
- use tools subdir and give it as java.endorsed.dirs (for java-1.4.2-bea e.g.)

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 0:2.7.1-6jpp_7fc
- stop scriptlet spew

* Wed Feb 22 2006 Rafael Schloming <rafaels@redhat.com> - 0:2.7.1-6jpp_6fc
- Updated to 2.7.1

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0:2.6.2-6jpp_5fc
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0:2.6.2-6jpp_4fc
- rebuilt for new gcc4.1 snapshot and glibc changes

* Thu Feb  2 2006 Archit Shah <ashah@redhat.com> 0:2.6.2-6jpp_3fc
- build xerces without using native code

* Mon Jan  9 2006 Archit Shah <ashah@redhat.com> 0:2.6.2-6jpp_2fc
- rebuilt for new gcj

* Wed Dec 21 2005 Jesse Keating <jkeating@redhat.com> 0:2.6.2-6jpp_1fc
- rebuilt for new gcj

* Tue Dec 13 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt for new gcj

* Fri Oct 07 2005 Ralph Apel <r.apel at r-apel.de> 0:2.7.1-1jpp
- Upgrade to 2.7.1

* Thu Jul 21 2005 Ralph Apel <r.apel at r-apel.de> 0:2.6.2-7jpp
- Include target jars-dom3
- Create new subpackage dom3

* Mon Jul 18 2005 Gary Benson <gbenson at redhat.com> 0:2.6.2-5jpp_2fc
- Build on ia64, ppc64, s390 and s390x.
- Switch to aot-compile-rpm (also BC-compiles samples).

* Wed Jul 13 2005 Gary Benson <gbenson at redhat.com> 0:2.6.2-6jpp
- Build with Sun JDK (from <gareth.armstrong at hp.com>).

* Wed Jun 15 2005 Gary Benson <gbenson at redhat.com> 0:2.6.2-5jpp_1fc
- Upgrade to 2.6.2-5jpp.

* Tue Jun 14 2005 Gary Benson <gbenson at redhat.com> 0:2.6.2-5jpp
- Remove the tools tarball, and build xjavac from source.
- Patch xjavac to fix the classpath under libgcj too.

* Fri Jun 10 2005 Gary Benson <gbenson@redhat.com> 0:2.6.2-4jpp_8fc
- Remove the tools tarball, and build xjavac from source.
- Replace classpath workaround to xjavac task and use
  xml-commons classes again (#152255).

* Thu May 26 2005 Gary Benson <gbenson@redhat.com> 0:2.6.2-4jpp_7fc
- Rearrange how BC-compiled stuff is built and installed.

* Mon May 23 2005 Gary Benson <gbenson@redhat.com> 0:2.6.2-4jpp_6fc
- Add alpha to the list of build architectures (#157522).
- Use absolute paths for rebuild-gcj-db.

* Thu May  5 2005 Gary Benson <gbenson@redhat.com> 0:2.6.2-4jpp_5fc
- Add dependencies for %%post and %%postun scriptlets (#156901).

* Fri Apr 29 2005 Gary Benson <gbenson@redhat.com> 0:2.6.2-4jpp_4fc
- BC-compile.

* Thu Apr 28 2005 Gary Benson <gbenson@redhat.com> 0:2.6.2-4jpp_3fc
- Revert xjavac classpath workaround, and patch to use libgcj's
  classes instead of those in xml-commons (#152255).

* Thu Apr 21 2005 Gary Benson <gbenson@redhat.com> 0:2.6.2-4jpp_2fc
- Add classpath workaround to xjavac task (#152255).

* Wed Jan 12 2005 Gary Benson <gbenson@redhat.com> 0:2.6.2-4jpp_1fc
- Reenable building of classes that require javax.swing (#130006).
- Sync with RHAPS.

* Mon Nov 15 2004 Fernando Nasser <fnasser@redhat.com>  0:2.6.2-4jpp_1rh
- Merge with upstream for 2.6.2 upgrade

* Thu Nov  4 2004 Gary Benson <gbenson@redhat.com> 0:2.6.2-2jpp_5fc
- Build into Fedora.

* Thu Oct 28 2004 Gary Benson <gbenson@redhat.com> 0:2.6.2-2jpp_4fc
- Bootstrap into Fedora.

* Fri Oct 1 2004 Andrew Overholt <overholt@redhat.com> 0:2.6.2-2jpp_4rh
- add coreutils BuildRequires

* Thu Sep 30 2004 Andrew Overholt <overholt@redhat.com> 0:2.6.2-2jpp_3rh
- Remove xml-commons-resolver as a Requires

* Thu Aug 26 2004 Ralph Apel <r.apel at r-apel.de> 0:2.6.2-4jpp
- Build with ant-1.6.2
- Dropped jikes requirement, built for 1.4.2

* Wed Jun 23 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2.6.2-3jpp
- Updated Patch #0 to fix breakage using BEA 1.4.2 SDK, new patch
  from <mwringe@redhat.com> and <vivekl@redhat.com>.

* Mon Jun 21 2004 Vivek Lakshmanan <vivekl@redhat.com> 0:2.6.2-2jpp_2rh
- Added new Source1 URL and added new %%setup to expand it under the
  expanded result of Source0.
- Updated Patch0 to fix version discrepancies.
- Added build requirement for xml-commons-apis
 
* Mon Jun 14 2004 Matt Wringe <mwringe@redhat.com> 0:2.6.2-2jpp_1rh
- Update to 2.6.2
- made patch names comformant

* Mon Mar 29 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2.6.2-2jpp
- Rebuilt with jikes 1.18 for java 1.3.1_11

* Fri Mar 26 2004 Frank Ch. Eigler <fche@redhat.com> 0:2.6.1-1jpp_2rh
- add RHUG upgrade cleanup

* Tue Mar 23 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2.6.2-1jpp
- 2.6.2

* Thu Mar 11 2004 Frank Ch. Eigler <fche@redhat.com> 0:2.6.1-1jpp_1rh
- RH vacuuming
- remove jikes dependency
- add nonjikes-cast.patch
