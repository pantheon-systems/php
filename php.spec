%{?scl:%scl_package php}
%{!?scl:%global pkg_name %{name}}

# API/ABI check
%global apiver      20121113
%global zendver     20121212
%global pdover      20080721
# Extension version
%global opcachever  7.0.3

# Adds -z now to the linker flags
%global _hardened_build 1

# version used for php embedded library soname
%global embed_version 5.5

%global mysql_sock %(mysql_config --socket 2>/dev/null || echo /var/lib/mysql/mysql.sock)

# Regression tests take a long time, you can skip 'em with this
%{!?runselftest: %{expand: %%global runselftest 1}}

# Use the arch-specific mysql_config binary to avoid mismatch with the
# arch detection heuristic used by bindir/mysql_config.
%global mysql_config %{_libdir}/mysql/mysql_config

# Build mysql/mysqli/pdo extensions using libmysqlclient or only mysqlnd
%global with_libmysql 0

# Build ZTS extension or only NTS
%global with_zts      1

%if 0%{?__isa_bits:1}
%global isasuffix -%{__isa_bits}
%else
%global isasuffix %nil
%endif

# /usr/sbin/apsx with httpd < 2.4 and defined as /usr/bin/apxs with httpd >= 2.4
%{!?_httpd_apxs:       %{expand: %%global _httpd_apxs       %%{_sbindir}/apxs}}
%{!?_httpd_mmn:        %{expand: %%global _httpd_mmn        %%(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo 0-0)}}
%{!?_httpd_confdir:    %{expand: %%global _httpd_confdir    %%{_sysconfdir}/httpd/conf.d}}
# /etc/httpd/conf.d with httpd < 2.4 and defined as /etc/httpd/conf.modules.d with httpd >= 2.4
%{!?_httpd_modconfdir: %{expand: %%global _httpd_modconfdir %%{_sysconfdir}/httpd/conf.d}}
%{!?_httpd_moddir:     %{expand: %%global _httpd_moddir     %%{_libdir}/httpd/modules}}
%{!?_httpd_contentdir: %{expand: %%global _httpd_contentdir /var/www}}

%global with_dtrace 1

# build with system libgd
%if 0%{?fedora} < 20
%global  with_libgd 0
%else
%global  with_libgd 1
%endif

%if 0%{?fedora} == 17 || 0%{?fedora} == 18 || 0%{?fedora} == 19 || 0%{?rhel} == 7
%global with_zip     1
%global with_libzip  1
%else
%global with_zip     0
%global with_libzip  0
%endif

%if 0%{?fedora} < 18 && 0%{?rhel} < 7
%global db_devel  db4-devel
%else
%global db_devel  libdb-devel
%endif

#global rcver RC3

Summary: PHP scripting language for creating dynamic web sites
Name: %{?scl_prefix}php
Version: 5.5.9
Release: 1%{?dist}
# All files licensed under PHP version 3.01, except
# Zend is licensed under Zend
# TSRM is licensed under BSD
License: PHP and Zend and BSD
Group: Development/Languages
URL: http://www.php.net/

# Need to download official tarball and strip non-free stuff
# wget http://www.php.net/distributions/php-%{version}%{?rcver}.tar.xz
# ./strip.sh %{version}
Source0: php-%{version}%{?rcver}-strip.tar.xz
Source1: php.conf
Source2: php.ini
Source3: macros.php
Source4: php-fpm.conf
Source5: php-fpm-www.conf
Source6: php-fpm.service
Source7: php-fpm.logrotate
Source8: php-fpm.sysconfig
Source9: php.modconf
Source10: php.ztsmodconf
Source11: strip.sh
# Configuration files for some extensions
Source50: opcache.ini
Source51: opcache-default.blacklist

# Build fixes
Patch5: php-5.2.0-includedir.patch
Patch6: php-5.2.4-embed.patch
Patch7: php-5.3.0-recode.patch
Patch8: php-5.4.7-libdb.patch

# Fixes for extension modules
# https://bugs.php.net/63171 no odbc call during timeout
Patch21: php-5.4.7-odbctimer.patch

# Functional changes
Patch40: php-5.4.0-dlopen.patch
Patch42: php-5.3.1-systzdata-v10.patch
# See http://bugs.php.net/53436
Patch43: php-5.4.0-phpize.patch
# Use system libzip instead of bundled one
Patch44: php-5.5.2-system-libzip.patch
# Use -lldap_r for OpenLDAP
Patch45: php-5.4.8-ldap_r.patch
# Make php_config.h constant across builds
Patch46: php-5.4.9-fixheader.patch
# drop "Configure command" from phpinfo output
Patch47: php-5.4.9-phpinfo.patch

# Upstream fixes

# Security fixes

# Fixes for tests


BuildRequires: bzip2-devel, curl-devel >= 7.9
BuildRequires: httpd-devel >= 2.0.46-1, pam-devel
BuildRequires: libstdc++-devel, openssl-devel
BuildRequires: sqlite-devel >= 3.6.0
BuildRequires: zlib-devel, smtpdaemon, libedit-devel
BuildRequires: pcre-devel >= 6.6
BuildRequires: bzip2, perl, libtool >= 1.4.3, gcc-c++
BuildRequires: libtool-ltdl-devel
%if %{with_libzip}
BuildRequires: libzip-devel >= 0.10
BuildRequires: libzip-devel <  0.11
%endif
%if %{with_dtrace}
BuildRequires: systemtap-sdt-devel
%endif

%if %{with_zts}
Obsoletes: %{?scl_prefix}php-zts < 5.3.7
Provides: %{?scl_prefix}php-zts = %{version}-%{release}
Provides: %{?scl_prefix}php-zts%{?_isa} = %{version}-%{release}
%endif

Requires: %{?scl_prefix}httpd-mmn = %{_httpd_mmn}
Provides: %{?scl_prefix}mod_php = %{version}-%{release}
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
# For backwards-compatibility, require php-cli for the time being:
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
# To ensure correct /var/lib/php/session ownership:
Requires(pre): httpd


# Don't provides extensions, which are not shared library, as .so
%{?filter_provides_in: %filter_provides_in %{_libdir}/php/modules/.*\.so$}
%{?filter_provides_in: %filter_provides_in %{_libdir}/php-zts/modules/.*\.so$}
%{?filter_provides_in: %filter_provides_in %{_httpd_moddir}/.*\.so$}
%{?filter_setup}

%description
PHP is an HTML-embedded scripting language. PHP attempts to make it
easy for developers to write dynamically generated web pages. PHP also
offers built-in database integration for several commercial and
non-commercial database management systems, so writing a
database-enabled webpage with PHP is fairly simple. The most common
use of PHP coding is probably as a replacement for CGI scripts. 

The php package contains the module (often referred to as mod_php)
which adds support for the PHP language to Apache HTTP Server.

%package cli
Group: Development/Languages
Summary: Command-line interface for PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-cgi = %{version}-%{release}, %{?scl_prefix}php-cgi%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pcntl, %{?scl_prefix}php-pcntl%{?_isa}
Provides: %{?scl_prefix}php-readline, %{?scl_prefix}php-readline%{?_isa}

%description cli
The php-cli package contains the command-line interface 
executing PHP scripts, /usr/bin/php, and the CGI interface.

%package fpm
Group: Development/Languages
Summary: PHP FastCGI Process Manager
# All files licensed under PHP version 3.01, except
# Zend is licensed under Zend
# TSRM and fpm are licensed under BSD
License: PHP and Zend and BSD
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires(pre): /usr/sbin/useradd
BuildRequires: systemd-units
BuildRequires: systemd-devel
Requires: systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description fpm
PHP-FPM (FastCGI Process Manager) is an alternative PHP FastCGI
implementation with some additional features useful for sites of
any size, especially busier sites.

%package common
Group: Development/Languages
Summary: Common files for PHP
# All files licensed under PHP version 3.01, except
# fileinfo is licensed under PHP version 3.0
# regex, libmagic are licensed under BSD
# main/snprintf.c, main/spprintf.c and main/rfc1867.c are ASL 1.0
License: PHP and BSD and ASL 1.0
# ABI/API check - Arch specific
Provides: %{?scl_prefix}php(api) = %{apiver}%{isasuffix}
Provides: %{?scl_prefix}php(zend-abi) = %{zendver}%{isasuffix}
Provides: %{?scl_prefix}php(language) = %{version}, php(language)%{?scl_prefix}%{?_isa} = %{version}
# Provides for all builtin/shared modules:
Provides: %{?scl_prefix}php-bz2, %{?scl_prefix}php-bz2%{?_isa}
Provides: %{?scl_prefix}php-calendar, %{?scl_prefix}php-calendar%{?_isa}
Provides: %{?scl_prefix}php-core = %{version}, %{?scl_prefix}php-core%{?_isa} = %{version}
Provides: %{?scl_prefix}php-ctype, %{?scl_prefix}php-ctype%{?_isa}
Provides: %{?scl_prefix}php-curl, %{?scl_prefix}php-curl%{?_isa}
Provides: %{?scl_prefix}php-date, %{?scl_prefix}php-date%{?_isa}
Provides: %{?scl_prefix}php-ereg, %{?scl_prefix}php-ereg%{?_isa}
Provides: %{?scl_prefix}php-exif, %{?scl_prefix}php-exif%{?_isa}
Provides: %{?scl_prefix}php-fileinfo, %{?scl_prefix}php-fileinfo%{?_isa}
Provides: %{?scl_prefix}php-filter, %{?scl_prefix}php-filter%{?_isa}
Provides: %{?scl_prefix}php-ftp, %{?scl_prefix}php-ftp%{?_isa}
Provides: %{?scl_prefix}php-gettext, %{?scl_prefix}php-gettext%{?_isa}
Provides: %{?scl_prefix}php-hash, %{?scl_prefix}php-hash%{?_isa}
Provides: %{?scl_prefix}php-mhash = %{version}, %{?scl_prefix}php-mhash%{?_isa} = %{version}
Provides: %{?scl_prefix}php-iconv, %{?scl_prefix}php-iconv%{?_isa}
Provides: %{?scl_prefix}php-libxml, %{?scl_prefix}php-libxml%{?_isa}
Provides: %{?scl_prefix}php-openssl, %{?scl_prefix}php-openssl%{?_isa}
Provides: %{?scl_prefix}php-phar, %{?scl_prefix}php-phar%{?_isa}
Provides: %{?scl_prefix}php-pcre, %{?scl_prefix}php-pcre%{?_isa}
Provides: %{?scl_prefix}php-reflection, %{?scl_prefix}php-reflection%{?_isa}
Provides: %{?scl_prefix}php-session, %{?scl_prefix}php-session%{?_isa}
Provides: %{?scl_prefix}php-sockets, %{?scl_prefix}php-sockets%{?_isa}
Provides: %{?scl_prefix}php-spl, %{?scl_prefix}php-spl%{?_isa}
Provides: %{?scl_prefix}php-standard = %{version}, %{?scl_prefix}php-standard%{?_isa} = %{version}
Provides: %{?scl_prefix}php-tokenizer, %{?scl_prefix}php-tokenizer%{?_isa}
# Temporary circular dep (to remove for bootstrap)
Requires: %{?scl_prefix}php-pecl-jsonc%{?_isa}
%if %{with_zip}
Provides: %{?scl_prefix}php-zip, %{?scl_prefix}php-zip%{?_isa}
Obsoletes: %{?scl_prefix}php-pecl-zip < 1.11
%endif
Provides: %{?scl_prefix}php-zlib, %{?scl_prefix}php-zlib%{?_isa}
Obsoletes: %{?scl_prefix}php-pecl-phar < 1.2.4
Obsoletes: %{?scl_prefix}php-pecl-Fileinfo < 1.0.5
Obsoletes: %{?scl_prefix}php-mhash < 5.3.0

%description common
The php-common package contains files used by both the php
package and the php-cli package.

%package devel
Group: Development/Libraries
Summary: Files needed for building PHP extensions
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}, autoconf, automake
Requires: pcre-devel%{?_isa}
%if %{with_zts}
Provides: %{?scl_prefix}php-zts-devel = %{version}-%{release}
Provides: %{?scl_prefix}php-zts-devel%{?_isa} = %{version}-%{release}
%endif
# Temporary circular dep (to remove for bootstrap)
Requires: %{?scl_prefix}php-pecl-jsonc-devel%{?_isa}

%description devel
The php-devel package contains the files needed for building PHP
extensions. If you need to compile your own PHP extensions, you will
need to install this package.

%package opcache
Summary:   The Zend OPcache
Group:     Development/Languages
License:   PHP
Requires:  %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Obsoletes: %{?scl_prefix}php-pecl-zendopcache
Provides:  %{?scl_prefix}php-pecl-zendopcache = %{opcachever}
Provides:  %{?scl_prefix}php-pecl-zendopcache%{?_isa} = %{opcachever}
Provides:  %{?scl_prefix}php-pecl(opcache) = %{opcachever}
Provides:  %{?scl_prefix}php-pecl(opcache)%{?_isa} = %{opcachever}

%description opcache
The Zend OPcache provides faster PHP execution through opcode caching and
optimization. It improves PHP performance by storing precompiled script
bytecode in the shared memory. This eliminates the stages of reading code from
the disk and compiling it on future access. In addition, it applies a few
bytecode optimization patterns that make code execution faster.

%package imap
Summary: A module for PHP applications that use IMAP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
BuildRequires: krb5-devel, openssl-devel, libc-client-devel

%description imap
The php-imap module will add IMAP (Internet Message Access Protocol)
support to PHP. IMAP is a protocol for retrieving and uploading e-mail
messages on mail servers. PHP is an HTML-embedded scripting language.

%package ldap
Summary: A module for PHP applications that use LDAP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
BuildRequires: cyrus-sasl-devel, openldap-devel, openssl-devel

%description ldap
The php-ldap adds Lightweight Directory Access Protocol (LDAP)
support to PHP. LDAP is a set of protocols for accessing directory
services over the Internet. PHP is an HTML-embedded scripting
language.

%package pdo
Summary: A database access abstraction module for PHP applications
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
# ABI/API check - Arch specific
Provides: %{?scl_prefix}php-pdo-abi  = %{pdover}%{isasuffix}
Provides: %{?scl_prefix}php(pdo-abi) = %{pdover}%{isasuffix}
Provides: %{?scl_prefix}php-sqlite3, %{?scl_prefix}php-sqlite3%{?_isa}
Provides: %{?scl_prefix}php-pdo_sqlite, %{?scl_prefix}php-pdo_sqlite%{?_isa}

%description pdo
The php-pdo package contains a dynamic shared object that will add
a database access abstraction layer to PHP.  This module provides
a common interface for accessing MySQL, PostgreSQL or other 
databases.

%if %{with_libmysql}

%package mysql
Summary: A module for PHP applications that use MySQL databases
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-pdo%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php_database
Provides: %{?scl_prefix}php-mysqli = %{version}-%{release}
Provides: %{?scl_prefix}php-mysqli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_mysql, %{?scl_prefix}php-pdo_mysql%{?_isa}
BuildRequires: %{?scl_prefix}mysql-devel >= 4.1.0
Conflicts: %{?scl_prefix}php-mysqlnd

%description mysql
The php-mysql package contains a dynamic shared object that will add
MySQL database support to PHP. MySQL is an object-relational database
management system. PHP is an HTML-embeddable scripting language. If
you need MySQL support for PHP applications, you will need to install
this package and the php package.
%endif

%package mysqlnd
Summary: A module for PHP applications that use MySQL databases
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-pdo%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php_database
Provides: %{?scl_prefix}php-mysql = %{version}-%{release}
Provides: %{?scl_prefix}php-mysql%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-mysqli = %{version}-%{release}
Provides: %{?scl_prefix}php-mysqli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_mysql, %{?scl_prefix}php-pdo_mysql%{?_isa}
%if ! %{with_libmysql}
Obsoletes: %{?scl_prefix}php-mysql < %{version}-%{release}
%endif

%description mysqlnd
The php-mysqlnd package contains a dynamic shared object that will add
MySQL database support to PHP. MySQL is an object-relational database
management system. PHP is an HTML-embeddable scripting language. If
you need MySQL support for PHP applications, you will need to install
this package and the php package.

This package use the MySQL Native Driver

%package pgsql
Summary: A PostgreSQL database module for PHP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-pdo%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php_database
Provides: %{?scl_prefix}php-pdo_pgsql, %{?scl_prefix}php-pdo_pgsql%{?_isa}
BuildRequires: krb5-devel, openssl-devel, postgresql-devel

%description pgsql
The php-pgsql package add PostgreSQL database support to PHP.
PostgreSQL is an object-relational database management
system that supports almost all SQL constructs. PHP is an
HTML-embedded scripting language. If you need back-end support for
PostgreSQL, you should install this package in addition to the main
php package.

%package process
Summary: Modules for PHP script using system process interfaces
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-posix, %{?scl_prefix}php-posix%{?_isa}
Provides: %{?scl_prefix}php-shmop, %{?scl_prefix}php-shmop%{?_isa}
Provides: %{?scl_prefix}php-sysvsem, %{?scl_prefix}php-sysvsem%{?_isa}
Provides: %{?scl_prefix}php-sysvshm, %{?scl_prefix}php-sysvshm%{?_isa}
Provides: %{?scl_prefix}php-sysvmsg, %{?scl_prefix}php-sysvmsg%{?_isa}

%description process
The php-process package contains dynamic shared objects which add
support to PHP using system interfaces for inter-process
communication.

%package odbc
Summary: A module for PHP applications that use ODBC databases
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# pdo_odbc is licensed under PHP version 3.0
License: PHP
Requires: %{?scl_prefix}php-pdo%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php_database
Provides: %{?scl_prefix}php-pdo_odbc, %{?scl_prefix}php-pdo_odbc%{?_isa}
BuildRequires: unixODBC-devel

%description odbc
The php-odbc package contains a dynamic shared object that will add
database support through ODBC to PHP. ODBC is an open specification
which provides a consistent API for developers to use for accessing
data sources (which are often, but not always, databases). PHP is an
HTML-embeddable scripting language. If you need ODBC support for PHP
applications, you will need to install this package and the php
package.

%package soap
Summary: A module for PHP applications that use the SOAP protocol
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
BuildRequires: libxml2-devel

%description soap
The php-soap package contains a dynamic shared object that will add
support to PHP for using the SOAP web services protocol.

%package interbase
Summary: A module for PHP applications that use Interbase/Firebird databases
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
BuildRequires:  firebird-devel
Requires: %{?scl_prefix}php-pdo%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php_database
Provides: %{?scl_prefix}php-firebird, %{?scl_prefix}php-firebird%{?_isa}
Provides: %{?scl_prefix}php-pdo_firebird, %{?scl_prefix}php-pdo_firebird%{?_isa}

%description interbase
The php-interbase package contains a dynamic shared object that will add
database support through Interbase/Firebird to PHP.

InterBase is the name of the closed-source variant of this RDBMS that was
developed by Borland/Inprise. 

Firebird is a commercially independent project of C and C++ programmers, 
technical advisors and supporters developing and enhancing a multi-platform 
relational database management system based on the source code released by 
Inprise Corp (now known as Borland Software Corp) under the InterBase Public
License.

%package snmp
Summary: A module for PHP applications that query SNMP-managed devices
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}, %{?scl_prefix}net-snmp
BuildRequires: net-snmp-devel

%description snmp
The php-snmp package contains a dynamic shared object that will add
support for querying SNMP devices to PHP.  PHP is an HTML-embeddable
scripting language. If you need SNMP support for PHP applications, you
will need to install this package and the php package.

%package xml
Summary: A module for PHP applications which use XML
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-dom, %{?scl_prefix}php-dom%{?_isa}
Provides: %{?scl_prefix}php-domxml, %{?scl_prefix}php-domxml%{?_isa}
Provides: %{?scl_prefix}php-simplexml, %{?scl_prefix}php-simplexml%{?_isa}
Provides: %{?scl_prefix}php-wddx, %{?scl_prefix}php-wddx%{?_isa}
Provides: %{?scl_prefix}php-xmlreader, %{?scl_prefix}php-xmlreader%{?_isa}
Provides: %{?scl_prefix}php-xmlwriter, %{?scl_prefix}php-xmlwriter%{?_isa}
Provides: %{?scl_prefix}php-xsl, %{?scl_prefix}php-xsl%{?_isa}
BuildRequires: libxslt-devel >= 1.0.18-1, libxml2-devel >= 2.4.14-1

%description xml
The php-xml package contains dynamic shared objects which add support
to PHP for manipulating XML documents using the DOM tree,
and performing XSL transformations on XML documents.

%package xmlrpc
Summary: A module for PHP applications which use the XML-RPC protocol
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libXMLRPC is licensed under BSD
License: PHP and BSD
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}

%description xmlrpc
The php-xmlrpc package contains a dynamic shared object that will add
support for the XML-RPC protocol to PHP.

%package mbstring
Summary: A module for PHP applications which need multi-byte string handling
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libmbfl is licensed under LGPLv2
# onigurama is licensed under BSD
# ucgendat is licensed under OpenLDAP
License: PHP and LGPLv2 and BSD and OpenLDAP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}

%description mbstring
The php-mbstring package contains a dynamic shared object that will add
support for multi-byte string handling to PHP.

%package gd
Summary: A module for PHP applications for using the gd graphics library
Group: Development/Languages
# All files licensed under PHP version 3.01
%if %{with_libgd}
License: PHP
%else
# bundled libgd is licensed under BSD
License: PHP and BSD
%endif
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
BuildRequires: t1lib-devel
%if %{with_libgd}
BuildRequires: gd-devel >= 2.1.0
%else
# Required to build the bundled GD library
BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
BuildRequires: freetype-devel
BuildRequires: libXpm-devel
BuildRequires: libvpx-devel
%endif

%description gd
The php-gd package contains a dynamic shared object that will add
support for using the gd graphics library to PHP.

%package bcmath
Summary: A module for PHP applications for using the bcmath library
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libbcmath is licensed under LGPLv2+
License: PHP and LGPLv2+
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}

%description bcmath
The php-bcmath package contains a dynamic shared object that will add
support for using the bcmath library to PHP.

%package gmp
Summary: A module for PHP applications for using the GNU MP library
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
BuildRequires: gmp-devel
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}

%description gmp
These functions allow you to work with arbitrary-length integers
using the GNU MP library.

%package dba
Summary: A database abstraction layer module for PHP applications
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
BuildRequires: %{db_devel}, tokyocabinet-devel
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}

%description dba
The php-dba package contains a dynamic shared object that will add
support for using the DBA database abstraction layer to PHP.

%package mcrypt
Summary: Standard PHP module provides mcrypt library support
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
BuildRequires: libmcrypt-devel

%description mcrypt
The php-mcrypt package contains a dynamic shared object that will add
support for using the mcrypt library to PHP.

%package tidy
Summary: Standard PHP module provides tidy library support
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
BuildRequires: libtidy-devel

%description tidy
The php-tidy package contains a dynamic shared object that will add
support for using the tidy library to PHP.

%package mssql
Summary: MSSQL database module for PHP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-pdo%{?_isa} = %{version}-%{release}
BuildRequires: freetds-devel
Provides: %{?scl_prefix}php-pdo_dblib, %{?scl_prefix}php-pdo_dblib%{?_isa}

%description mssql
The php-mssql package contains a dynamic shared object that will
add MSSQL database support to PHP.  It uses the TDS (Tabular
DataStream) protocol through the freetds library, hence any
database server which supports TDS can be accessed.

%package embedded
Summary: PHP library for embedding in applications
Group: System Environment/Libraries
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
# doing a real -devel package for just the .so symlink is a bit overkill
Provides: %{?scl_prefix}php-embedded-devel = %{version}-%{release}
Provides: %{?scl_prefix}php-embedded-devel%{?_isa} = %{version}-%{release}

%description embedded
The php-embedded package contains a library which can be embedded
into applications to provide PHP scripting language support.

%package pspell
Summary: A module for PHP applications for using pspell interfaces
Group: System Environment/Libraries
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
BuildRequires: aspell-devel >= 0.50.0

%description pspell
The php-pspell package contains a dynamic shared object that will add
support for using the pspell library to PHP.

%package recode
Summary: A module for PHP applications for using the recode library
Group: System Environment/Libraries
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
BuildRequires: recode-devel

%description recode
The php-recode package contains a dynamic shared object that will add
support for using the recode library to PHP.

%package intl
Summary: Internationalization extension for PHP applications
Group: System Environment/Libraries
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
BuildRequires: libicu-devel >= 4.0

%description intl
The php-intl package contains a dynamic shared object that will add
support for using the ICU library to PHP.

%package enchant
Summary: Enchant spelling extension for PHP applications
Group: System Environment/Libraries
# All files licensed under PHP version 3.0
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
BuildRequires: enchant-devel >= 1.2.4

%description enchant
The php-enchant package contains a dynamic shared object that will add
support for using the enchant library to PHP.

%prep
%setup -q -n php-%{version}%{?rcver}

%patch5 -p1 -b .includedir
%patch6 -p1 -b .embed
%patch7 -p1 -b .recode
%patch8 -p1 -b .libdb

%patch21 -p1 -b .odbctimer

%patch40 -p1 -b .dlopen
%patch42 -p1 -b .systzdata
%patch43 -p1 -b .headers
%if %{with_libzip}
%patch44 -p1 -b .systzip
%endif
%if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
%patch45 -p1 -b .ldap_r
%endif
%patch46 -p1 -b .fixheader
%patch47 -p1 -b .phpinfo


# Prevent %%doc confusion over LICENSE files
cp Zend/LICENSE Zend/ZEND_LICENSE
cp TSRM/LICENSE TSRM_LICENSE
cp ext/ereg/regex/COPYRIGHT regex_COPYRIGHT
%if ! %{with_libgd}
cp ext/gd/libgd/README libgd_README
cp ext/gd/libgd/COPYING libgd_COPYING
%endif
cp sapi/fpm/LICENSE fpm_LICENSE
cp ext/mbstring/libmbfl/LICENSE libmbfl_LICENSE
cp ext/mbstring/oniguruma/COPYING oniguruma_COPYING
cp ext/mbstring/ucgendat/OPENLDAP_LICENSE ucgendat_LICENSE
cp ext/fileinfo/libmagic/LICENSE libmagic_LICENSE
cp ext/phar/LICENSE phar_LICENSE
cp ext/bcmath/libbcmath/COPYING.LIB libbcmath_COPYING

# Multiple builds for multiple SAPIs
mkdir build-cgi build-apache build-embedded \
%if %{with_zts}
    build-zts build-ztscli \
%endif
    build-fpm

# ----- Manage known as failed test -------
# affected by systzdata patch
rm -f ext/date/tests/timezone_location_get.phpt
# fails sometime
rm -f ext/sockets/tests/mcast_ipv?_recv.phpt

# Safety check for API version change.
pver=$(sed -n '/#define PHP_VERSION /{s/.* "//;s/".*$//;p}' main/php_version.h)
if test "x${pver}" != "x%{version}%{?rcver}"; then
   : Error: Upstream PHP version is now ${pver}, expecting %{version}%{?rcver}.
   : Update the version/rcver macros and rebuild.
   exit 1
fi

vapi=`sed -n '/#define PHP_API_VERSION/{s/.* //;p}' main/php.h`
if test "x${vapi}" != "x%{apiver}"; then
   : Error: Upstream API version is now ${vapi}, expecting %{apiver}.
   : Update the apiver macro and rebuild.
   exit 1
fi

vzend=`sed -n '/#define ZEND_MODULE_API_NO/{s/^[^0-9]*//;p;}' Zend/zend_modules.h`
if test "x${vzend}" != "x%{zendver}"; then
   : Error: Upstream Zend ABI version is now ${vzend}, expecting %{zendver}.
   : Update the zendver macro and rebuild.
   exit 1
fi

# Safety check for PDO ABI version change
vpdo=`sed -n '/#define PDO_DRIVER_API/{s/.*[ 	]//;p}' ext/pdo/php_pdo_driver.h`
if test "x${vpdo}" != "x%{pdover}"; then
   : Error: Upstream PDO ABI version is now ${vpdo}, expecting %{pdover}.
   : Update the pdover macro and rebuild.
   exit 1
fi

# Check for some extension version
ver=$(sed -n '/#define ACCELERATOR_VERSION /{s/.* "//;s/".*$//;p}' ext/opcache/ZendAccelerator.h)
if test "$ver" != "%{opcachever}"; then
   : Error: Upstream PHAR version is now ${ver}, expecting %{opcachever}.
   : Update the opcachever macro and rebuild.
   exit 1
fi

# https://bugs.php.net/63362 - Not needed but installed headers.
# Drop some Windows specific headers to avoid installation,
# before build to ensure they are really not needed.
rm -f TSRM/tsrm_win32.h \
      TSRM/tsrm_config.w32.h \
      Zend/zend_config.w32.h \
      ext/mysqlnd/config-win.h \
      ext/standard/winver.h \
      main/win32_internal_function_disabled.h \
      main/win95nt.h

# Fix some bogus permissions
find . -name \*.[ch] -exec chmod 644 {} \;
chmod 644 README.*

# php-fpm configuration files for tmpfiles.d
echo "d /run/php-fpm 755 root root" >php-fpm.tmpfiles

# Some extensions have their own configuration file
cp %{SOURCE50} .

%build
# aclocal workaround - to be improved
cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >>aclocal.m4

# Force use of system libtool:
libtoolize --force --copy
cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >build/libtool.m4

# Regenerate configure scripts (patches change config.m4's)
touch configure.in
./buildconf --force

CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-pointer-sign"
export CFLAGS

# Install extension modules in %{_libdir}/php/modules.
EXTENSION_DIR=%{_libdir}/php/modules; export EXTENSION_DIR

# Set PEAR_INSTALLDIR to ensure that the hard-coded include_path
# includes the PEAR directory even though pear is packaged
# separately.
PEAR_INSTALLDIR=%{_datadir}/pear; export PEAR_INSTALLDIR

# Shell function to configure and build a PHP tree.
build() {
# Old/recent bison version seems to produce a broken parser;
# upstream uses GNU Bison 2.3. Workaround:
mkdir Zend && cp ../Zend/zend_{language,ini}_{parser,scanner}.[ch] Zend

# Always static:
# date, ereg, filter, libxml, reflection, spl: not supported
# hash: for PHAR_SIG_SHA256 and PHAR_SIG_SHA512
# session: dep on hash, used by soap and wddx
# pcre: used by filter, zip
# pcntl, readline: only used by CLI sapi
# openssl: for PHAR_SIG_OPENSSL
# zlib: used by image

ln -sf ../configure
%{?scl:scl enable %{scl} "}
%configure \
    --cache-file=../config.cache \
    --with-libdir=%{_lib} \
    --with-config-file-path=%{_sysconfdir} \
    --with-config-file-scan-dir=%{_sysconfdir}/php.d \
    --disable-debug \
    --with-pic \
    --disable-rpath \
    --without-pear \
    --with-exec-dir=%{_bindir} \
    --with-freetype-dir=%{_prefix} \
    --with-png-dir=%{_prefix} \
    --with-xpm-dir=%{_prefix} \
    --with-vpx-dir=%{_prefix} \
    --enable-gd-native-ttf \
    --with-t1lib=%{_prefix} \
    --without-gdbm \
    --with-jpeg-dir=%{_prefix} \
    --with-openssl \
    --with-pcre-regex=%{_prefix} \
    --with-zlib \
    --with-layout=GNU \
    --with-kerberos \
    --with-libxml-dir=%{_prefix} \
    --with-system-tzdata \
    --with-mhash \
%if %{with_dtrace}
    --enable-dtrace \
%endif
    $*
%{?scl:"}
if test $? != 0; then 
  tail -500 config.log
  : configure failed
  exit 1
fi

%{?scl:scl enable %{scl} "}
make %{?_smp_mflags}
%{?scl:"}
}

# Build /usr/bin/php-cgi with the CGI SAPI, and most shared extensions
pushd build-cgi

build --libdir=%{_libdir}/php \
      --enable-pcntl \
      --enable-opcache \
      --with-imap=shared --with-imap-ssl \
      --enable-mbstring=shared \
      --enable-mbregex \
%if %{with_libgd}
      --with-gd=shared,%{_prefix} \
%else
      --with-gd=shared \
%endif
      --with-gmp=shared \
      --enable-calendar=shared \
      --enable-bcmath=shared \
      --with-bz2=shared \
      --enable-ctype=shared \
      --enable-dba=shared --with-db4=%{_prefix} \
                          --with-tcadb=%{_prefix} \
      --enable-exif=shared \
      --enable-ftp=shared \
      --with-gettext=shared \
      --with-iconv=shared \
      --enable-sockets=shared \
      --enable-tokenizer=shared \
      --with-xmlrpc=shared \
      --with-ldap=shared --with-ldap-sasl \
      --enable-mysqlnd=shared \
      --with-mysql=shared,mysqlnd \
      --with-mysqli=shared,mysqlnd \
      --with-mysql-sock=%{mysql_sock} \
      --with-interbase=shared,%{_libdir}/firebird \
      --with-pdo-firebird=shared,%{_libdir}/firebird \
      --enable-dom=shared \
      --with-pgsql=shared \
      --enable-simplexml=shared \
      --enable-xml=shared \
      --enable-wddx=shared \
      --with-snmp=shared,%{_prefix} \
      --enable-soap=shared \
      --with-xsl=shared,%{_prefix} \
      --enable-xmlreader=shared --enable-xmlwriter=shared \
      --with-curl=shared,%{_prefix} \
      --enable-pdo=shared \
      --with-pdo-odbc=shared,unixODBC,%{_prefix} \
      --with-pdo-mysql=shared,mysqlnd \
      --with-pdo-pgsql=shared,%{_prefix} \
      --with-pdo-sqlite=shared,%{_prefix} \
      --with-pdo-dblib=shared,%{_prefix} \
      --with-sqlite3=shared,%{_prefix} \
%if %{with_zip}
      --enable-zip=shared \
%if %{with_libzip}
      --with-libzip \
%endif
%endif
      --without-readline \
      --with-libedit \
      --with-pspell=shared \
      --enable-phar=shared \
      --with-mcrypt=shared,%{_prefix} \
      --with-tidy=shared,%{_prefix} \
      --with-mssql=shared,%{_prefix} \
      --enable-sysvmsg=shared --enable-sysvshm=shared --enable-sysvsem=shared \
      --enable-shmop=shared \
      --enable-posix=shared \
      --with-unixODBC=shared,%{_prefix} \
      --enable-fileinfo=shared \
      --enable-intl=shared \
      --with-icu-dir=%{_prefix} \
      --with-enchant=shared,%{_prefix} \
      --with-recode=shared,%{_prefix}
popd

without_shared="--without-gd \
      --disable-dom --disable-dba --without-unixODBC \
      --disable-opcache \
      --disable-xmlreader --disable-xmlwriter \
      --without-sqlite3 --disable-phar --disable-fileinfo \
      --without-pspell --disable-wddx \
      --without-curl --disable-posix --disable-xml \
      --disable-simplexml --disable-exif --without-gettext \
      --without-iconv --disable-ftp --without-bz2 --disable-ctype \
      --disable-shmop --disable-sockets --disable-tokenizer \
      --disable-sysvmsg --disable-sysvshm --disable-sysvsem"

# Build Apache module, and the CLI SAPI, /usr/bin/php
pushd build-apache
build --with-apxs2=%{_httpd_apxs} \
      --libdir=%{_libdir}/php \
%if %{with_libmysql}
      --enable-pdo=shared \
      --with-mysql=shared,%{_prefix} \
      --with-mysqli=shared,%{mysql_config} \
      --with-pdo-mysql=shared,%{mysql_config} \
      --without-pdo-sqlite \
%else
      --without-mysql \
      --disable-pdo \
%endif
      ${without_shared}
popd

# Build php-fpm
pushd build-fpm
build --enable-fpm \
      --with-fpm-systemd \
      --libdir=%{_libdir}/php \
      --without-mysql \
      --disable-pdo \
      ${without_shared}
popd

# Build for inclusion as embedded script language into applications,
# /usr/lib[64]/libphp5.so
pushd build-embedded
build --enable-embed \
      --without-mysql --disable-pdo \
      ${without_shared}
popd

%if %{with_zts}
# Build a special thread-safe (mainly for modules)
pushd build-ztscli

EXTENSION_DIR=%{_libdir}/php-zts/modules
build --includedir=%{_includedir}/php-zts \
      --libdir=%{_libdir}/php-zts \
      --enable-maintainer-zts \
      --with-config-file-scan-dir=%{_sysconfdir}/php-zts.d \
      --enable-pcntl \
      --enable-opcache \
      --with-imap=shared --with-imap-ssl \
      --enable-mbstring=shared \
      --enable-mbregex \
%if %{with_libgd}
      --with-gd=shared,%{_prefix} \
%else
      --with-gd=shared \
%endif
      --with-gmp=shared \
      --enable-calendar=shared \
      --enable-bcmath=shared \
      --with-bz2=shared \
      --enable-ctype=shared \
      --enable-dba=shared --with-db4=%{_prefix} \
                          --with-tcadb=%{_prefix} \
      --with-gettext=shared \
      --with-iconv=shared \
      --enable-sockets=shared \
      --enable-tokenizer=shared \
      --enable-exif=shared \
      --enable-ftp=shared \
      --with-xmlrpc=shared \
      --with-ldap=shared --with-ldap-sasl \
      --enable-mysqlnd=shared \
      --with-mysql=shared,mysqlnd \
      --with-mysqli=shared,mysqlnd \
      --with-mysql-sock=%{mysql_sock} \
      --enable-mysqlnd-threading \
      --with-interbase=shared,%{_libdir}/firebird \
      --with-pdo-firebird=shared,%{_libdir}/firebird \
      --enable-dom=shared \
      --with-pgsql=shared \
      --enable-simplexml=shared \
      --enable-xml=shared \
      --enable-wddx=shared \
      --with-snmp=shared,%{_prefix} \
      --enable-soap=shared \
      --with-xsl=shared,%{_prefix} \
      --enable-xmlreader=shared --enable-xmlwriter=shared \
      --with-curl=shared,%{_prefix} \
      --enable-pdo=shared \
      --with-pdo-odbc=shared,unixODBC,%{_prefix} \
      --with-pdo-mysql=shared,mysqlnd \
      --with-pdo-pgsql=shared,%{_prefix} \
      --with-pdo-sqlite=shared,%{_prefix} \
      --with-pdo-dblib=shared,%{_prefix} \
      --with-sqlite3=shared,%{_prefix} \
%if %{with_zip}
      --enable-zip=shared \
%if %{with_libzip}
      --with-libzip \
%endif
%endif
      --without-readline \
      --with-libedit \
      --with-pspell=shared \
      --enable-phar=shared \
      --with-mcrypt=shared,%{_prefix} \
      --with-tidy=shared,%{_prefix} \
      --with-mssql=shared,%{_prefix} \
      --enable-sysvmsg=shared --enable-sysvshm=shared --enable-sysvsem=shared \
      --enable-shmop=shared \
      --enable-posix=shared \
      --with-unixODBC=shared,%{_prefix} \
      --enable-fileinfo=shared \
      --enable-intl=shared \
      --with-icu-dir=%{_prefix} \
      --with-enchant=shared,%{_prefix} \
      --with-recode=shared,%{_prefix}
popd

# Build a special thread-safe Apache SAPI
pushd build-zts
build --with-apxs2=%{_httpd_apxs} \
      --includedir=%{_includedir}/php-zts \
      --libdir=%{_libdir}/php-zts \
      --enable-maintainer-zts \
      --with-config-file-scan-dir=%{_sysconfdir}/php-zts.d \
%if %{with_libmysql}
      --enable-pdo=shared \
      --with-mysql=shared,%{_prefix} \
      --with-mysqli=shared,%{mysql_config} \
      --with-pdo-mysql=shared,%{mysql_config} \
      --without-pdo-sqlite \
%else
      --without-mysql \
      --disable-pdo \
%endif
      ${without_shared}
popd

### NOTE!!! EXTENSION_DIR was changed for the -zts build, so it must remain
### the last SAPI to be built.
%endif

%check
%if %runselftest

# Increase stack size (required by bug54268.phpt)
ulimit -s 32712

cd build-apache
# Run tests, using the CLI SAPI
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
export SKIP_ONLINE_TESTS=1
unset TZ LANG LC_ALL
if ! make test; then
  set +x
  for f in $(find .. -name \*.diff -type f -print); do
    if ! grep -q XFAIL "${f/.diff/.phpt}"
    then
      echo "TEST FAILURE: $f --"
      cat "$f"
      echo -e "\n-- $f result ends."
    fi
  done
  set -x
  #exit 1
fi
unset NO_INTERACTION REPORT_EXIT_STATUS MALLOC_CHECK_
%endif

%install
%if %{with_zts}
# Install the extensions for the ZTS version
%{?scl:scl enable %{scl} - << \EOF}
make -C build-ztscli install \
     INSTALL_ROOT=$RPM_BUILD_ROOT
%{?scl:EOF}

# rename extensions build with mysqlnd
mv $RPM_BUILD_ROOT%{_libdir}/php-zts/modules/mysql.so \
   $RPM_BUILD_ROOT%{_libdir}/php-zts/modules/mysqlnd_mysql.so
mv $RPM_BUILD_ROOT%{_libdir}/php-zts/modules/mysqli.so \
   $RPM_BUILD_ROOT%{_libdir}/php-zts/modules/mysqlnd_mysqli.so
mv $RPM_BUILD_ROOT%{_libdir}/php-zts/modules/pdo_mysql.so \
   $RPM_BUILD_ROOT%{_libdir}/php-zts/modules/pdo_mysqlnd.so

%if %{with_libmysql}
# Install the extensions for the ZTS version modules for libmysql
%{?scl:scl enable %{scl} - << \EOF}
make -C build-zts install-modules \
     INSTALL_ROOT=$RPM_BUILD_ROOT
%{?scl:EOF}
%endif

# rename ZTS binary
mv $RPM_BUILD_ROOT%{_bindir}/php        $RPM_BUILD_ROOT%{_bindir}/zts-php
mv $RPM_BUILD_ROOT%{_bindir}/phpize     $RPM_BUILD_ROOT%{_bindir}/zts-phpize
mv $RPM_BUILD_ROOT%{_bindir}/php-config $RPM_BUILD_ROOT%{_bindir}/zts-php-config
%endif

# Install the version for embedded script language in applications + php_embed.h
%{?scl:scl enable %{scl} - << \EOF}
make -C build-embedded install-sapi install-headers \
     INSTALL_ROOT=$RPM_BUILD_ROOT
%{?scl:EOF}

# Install the php-fpm binary
%{?scl:scl enable %{scl} - << \EOF}
make -C build-fpm install-fpm \
     INSTALL_ROOT=$RPM_BUILD_ROOT
%{?scl:EOF}

# Install everything from the CGI SAPI build
%{?scl:scl enable %{scl} - << \EOF}
make -C build-cgi install \
     INSTALL_ROOT=$RPM_BUILD_ROOT
%{?scl:EOF}

# rename extensions build with mysqlnd
mv $RPM_BUILD_ROOT%{_libdir}/php/modules/mysql.so \
   $RPM_BUILD_ROOT%{_libdir}/php/modules/mysqlnd_mysql.so
mv $RPM_BUILD_ROOT%{_libdir}/php/modules/mysqli.so \
   $RPM_BUILD_ROOT%{_libdir}/php/modules/mysqlnd_mysqli.so
mv $RPM_BUILD_ROOT%{_libdir}/php/modules/pdo_mysql.so \
   $RPM_BUILD_ROOT%{_libdir}/php/modules/pdo_mysqlnd.so

%if %{with_libmysql}
# Install the mysql extension build with libmysql
%{?scl:scl enable %{scl} - << \EOF}
make -C build-apache install-modules \
     INSTALL_ROOT=$RPM_BUILD_ROOT
%{?scl:EOF}
%endif

# Install the default configuration file and icons
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/php.ini
install -m 755 -d $RPM_BUILD_ROOT%{_httpd_contentdir}/icons
install -m 644 php.gif $RPM_BUILD_ROOT%{_httpd_contentdir}/icons/php.gif

# For third-party packaging:
install -m 755 -d $RPM_BUILD_ROOT%{_datadir}/php

# install the DSO
install -m 755 -d $RPM_BUILD_ROOT%{_httpd_moddir}
install -m 755 build-apache/libs/libphp5.so $RPM_BUILD_ROOT%{_httpd_moddir}

%if %{with_zts}
# install the ZTS DSO
install -m 755 build-zts/libs/libphp5.so $RPM_BUILD_ROOT%{_httpd_moddir}/libphp5-zts.so
%endif

# Apache config fragment
%if "%{_httpd_modconfdir}" == "%{_httpd_confdir}"
# Single config file with httpd < 2.4 (fedora <= 17)
install -D -m 644 %{SOURCE9} $RPM_BUILD_ROOT%{_httpd_confdir}/php.conf
%if %{with_zts}
cat %{SOURCE10} >>$RPM_BUILD_ROOT%{_httpd_confdir}/php.conf
%endif
cat %{SOURCE1} >>$RPM_BUILD_ROOT%{_httpd_confdir}/php.conf
%else
# Dual config file with httpd >= 2.4 (fedora >= 18)
install -D -m 644 %{SOURCE9} $RPM_BUILD_ROOT%{_httpd_modconfdir}/10-php.conf
%if %{with_zts}
cat %{SOURCE10} >>$RPM_BUILD_ROOT%{_httpd_modconfdir}/10-php.conf
%endif

install -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_httpd_confdir}/php.conf
%endif

install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php.d
%if %{with_zts}
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php-zts.d
%endif
install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/lib/php
install -m 700 -d $RPM_BUILD_ROOT%{_localstatedir}/lib/php/session
install -m 700 -d $RPM_BUILD_ROOT%{_localstatedir}/lib/php/wsdlcache

# PHP-FPM stuff
# Log
install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/log/php-fpm
install -m 755 -d $RPM_BUILD_ROOT/run/php-fpm
# Config
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d
install -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.conf
install -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/www.conf
mv $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.conf.default .
# tmpfiles.d
install -m 755 -d $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d
install -m 644 php-fpm.tmpfiles $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d/php-fpm.conf
# install systemd unit files and scripts for handling server startup
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/systemd/system/php-fpm.service.d
install -m 755 -d $RPM_BUILD_ROOT%{_unitdir}
install -m 644 %{SOURCE6} $RPM_BUILD_ROOT%{_unitdir}/
# LogRotate
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/php-fpm
# Environment file
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE8} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/php-fpm

# Fix the link
(cd $RPM_BUILD_ROOT%{_bindir}; ln -sfn phar.phar phar)

# Generate files lists and stub .ini files for each subpackage
for mod in pgsql odbc ldap snmp xmlrpc imap \
    mysqlnd mysqlnd_mysql mysqlnd_mysqli pdo_mysqlnd \
    mbstring gd dom xsl soap bcmath dba xmlreader xmlwriter \
    simplexml bz2 calendar ctype exif ftp gettext gmp iconv \
    sockets tokenizer opcache \
    pdo pdo_pgsql pdo_odbc pdo_sqlite \
    sqlite3  interbase pdo_firebird \
    enchant phar fileinfo intl \
    mcrypt tidy pdo_dblib mssql pspell curl wddx \
    posix shmop sysvshm sysvsem sysvmsg recode xml \
%if %{with_libmysql}
    mysql mysqli pdo_mysql \
%endif
%if %{with_zip}
    zip \
%endif
    ; do
    # for extension load order
    if [ "$mod" = "wddx" ]
    then   ini=xml_${mod}.ini
    else   ini=${mod}.ini
    fi
    # some extensions have their own config file
    if [ -f ${ini} ]; then
      cp -p ${ini} $RPM_BUILD_ROOT%{_sysconfdir}/php.d/${ini}
      cp -p ${ini} $RPM_BUILD_ROOT%{_sysconfdir}/php-zts.d/${ini}
    else
      cat > $RPM_BUILD_ROOT%{_sysconfdir}/php.d/${ini} <<EOF
; Enable ${mod} extension module
extension=${mod}.so
EOF
%if %{with_zts}
      cat > $RPM_BUILD_ROOT%{_sysconfdir}/php-zts.d/${ini} <<EOF
; Enable ${mod} extension module
extension=${mod}.so
EOF
%endif
    fi
    cat > files.${mod} <<EOF
%attr(755,root,root) %{_libdir}/php/modules/${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/php.d/${ini}
%if %{with_zts}
%attr(755,root,root) %{_libdir}/php-zts/modules/${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/php-zts.d/${ini}
%endif
EOF
done

# The dom, xsl and xml* modules are all packaged in php-xml
cat files.dom files.xsl files.xml{reader,writer} files.wddx \
    files.simplexml >> files.xml

# The mysql and mysqli modules are both packaged in php-mysql
%if %{with_libmysql}
cat files.mysqli >> files.mysql
cat files.pdo_mysql >> files.mysql
%endif

# mysqlnd
cat files.mysqlnd_mysql \
    files.mysqlnd_mysqli \
    files.pdo_mysqlnd \
    >> files.mysqlnd

# Split out the PDO modules
cat files.pdo_dblib >> files.mssql
cat files.pdo_pgsql >> files.pgsql
cat files.pdo_odbc >> files.odbc
cat files.pdo_firebird >> files.interbase

# sysv* and posix in packaged in php-process
cat files.shmop files.sysv* files.posix > files.process

# Package sqlite3 and pdo_sqlite with pdo; isolating the sqlite dependency
# isn't useful at this time since rpm itself requires sqlite.
cat files.pdo_sqlite >> files.pdo
cat files.sqlite3 >> files.pdo

# Package zip, curl, phar and fileinfo in -common.
cat files.curl files.phar files.fileinfo \
    files.exif files.gettext files.iconv files.calendar \
    files.ftp files.bz2 files.ctype files.sockets \
    files.tokenizer > files.common
%if %{with_zip}
cat files.zip >> files.common
%endif

# The default Zend OPcache blacklist file
install -m 644 %{SOURCE51} $RPM_BUILD_ROOT%{_sysconfdir}/php.d/opcache-default.blacklist
install -m 644 %{SOURCE51} $RPM_BUILD_ROOT%{_sysconfdir}/php-zts.d/opcache-default.blacklist
sed -e '/blacklist_filename/s/php.d/php-zts.d/' \
    -i $RPM_BUILD_ROOT%{_sysconfdir}/php-zts.d/opcache.ini

# Install the macros file:
sed -e "s/@PHP_APIVER@/%{apiver}%{isasuffix}/" \
    -e "s/@PHP_ZENDVER@/%{zendver}%{isasuffix}/" \
    -e "s/@PHP_PDOVER@/%{pdover}%{isasuffix}/" \
    -e "s/@PHP_VERSION@/%{version}/" \
%if ! %{with_zts}
    -e "/zts/d" \
%endif
    < %{SOURCE3} > macros.php
install -m 644 -D macros.php \
           $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d/macros.php

# Remove unpackaged files
rm -rf $RPM_BUILD_ROOT%{_libdir}/php/modules/*.a \
       $RPM_BUILD_ROOT%{_libdir}/php-zts/modules/*.a \
       $RPM_BUILD_ROOT%{_bindir}/{phptar} \
       $RPM_BUILD_ROOT%{_datadir}/pear \
       $RPM_BUILD_ROOT%{_libdir}/libphp5.la

# Remove irrelevant docs
rm -f README.{Zeus,QNX,CVS-RULES}


%pre fpm
# Add the "apache" user as we don't require httpd
getent group  apache >/dev/null || \
  groupadd -g 48 -r apache
getent passwd apache >/dev/null || \
  useradd -r -u 48 -g apache -s /sbin/nologin \
    -d %{_httpd_contentdir} -c "Apache" apache
exit 0

%post fpm
%systemd_post php-fpm.service

%preun fpm
%systemd_preun php-fpm.service

%postun fpm
%systemd_postun_with_restart php-fpm.service

%post embedded -p /sbin/ldconfig
%postun embedded -p /sbin/ldconfig

%files
%{_httpd_moddir}/libphp5.so
%if %{with_zts}
%{_httpd_moddir}/libphp5-zts.so
%endif
%attr(0770,root,apache) %dir %{_localstatedir}/lib/php/session
%attr(0770,root,apache) %dir %{_localstatedir}/lib/php/wsdlcache
%config(noreplace) %{_httpd_confdir}/php.conf
%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
%config(noreplace) %{_httpd_modconfdir}/10-php.conf
%endif
%{_httpd_contentdir}/icons/php.gif

%files common -f files.common
%doc CODING_STANDARDS CREDITS EXTENSIONS LICENSE NEWS README*
%doc Zend/ZEND_* TSRM_LICENSE regex_COPYRIGHT
%doc libmagic_LICENSE
%doc phar_LICENSE
%doc php.ini-*
%config(noreplace) %{_sysconfdir}/php.ini
%dir %{_sysconfdir}/php.d
%dir %{_libdir}/php
%dir %{_libdir}/php/modules
%if %{with_zts}
%dir %{_sysconfdir}/php-zts.d
%dir %{_libdir}/php-zts
%dir %{_libdir}/php-zts/modules
%endif
%dir %{_localstatedir}/lib/php
%dir %{_datadir}/php

%files cli
%{_bindir}/php
%{_bindir}/php-cgi
%{_bindir}/phar.phar
%{_bindir}/phar
# provides phpize here (not in -devel) for pecl command
%{_bindir}/phpize
%{_mandir}/man1/php.1*
%{_mandir}/man1/php-cgi.1*
%{_mandir}/man1/phar.1*
%{_mandir}/man1/phar.phar.1*
%{_mandir}/man1/phpize.1*
%doc sapi/cgi/README* sapi/cli/README

%files fpm
%doc php-fpm.conf.default
%doc fpm_LICENSE
%config(noreplace) %{_sysconfdir}/php-fpm.conf
%config(noreplace) %{_sysconfdir}/php-fpm.d/www.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/php-fpm
%config(noreplace) %{_sysconfdir}/sysconfig/php-fpm
%{_prefix}/lib/tmpfiles.d/php-fpm.conf
%{_unitdir}/php-fpm.service
%{_sbindir}/php-fpm
%dir %{_sysconfdir}/systemd/system/php-fpm.service.d
%dir %{_sysconfdir}/php-fpm.d
# log owned by apache for log
%attr(770,apache,root) %dir %{_localstatedir}/log/php-fpm
%dir /run/php-fpm
%{_mandir}/man8/php-fpm.8*
%dir %{_datadir}/fpm
%{_datadir}/fpm/status.html

%files devel
%{_bindir}/php-config
%{_includedir}/php
%{_libdir}/php/build
%if %{with_zts}
%{_bindir}/zts-php-config
%{_includedir}/php-zts
%{_bindir}/zts-phpize
# usefull only to test other module during build
%{_bindir}/zts-php
%{_libdir}/php-zts/build
%endif
%{_mandir}/man1/php-config.1*
%{_rpmconfigdir}/macros.d/macros.php

%files embedded
%{_libdir}/libphp5.so
%{_libdir}/libphp5-%{embed_version}.so

%files pgsql -f files.pgsql
%if %{with_libmysql}

%files mysql -f files.mysql
%endif

%files odbc -f files.odbc

%files imap -f files.imap

%files ldap -f files.ldap

%files snmp -f files.snmp

%files xml -f files.xml

%files xmlrpc -f files.xmlrpc

%files mbstring -f files.mbstring
%doc libmbfl_LICENSE
%doc oniguruma_COPYING
%doc ucgendat_LICENSE

%files gd -f files.gd
%if ! %{with_libgd}
%doc libgd_README
%doc libgd_COPYING
%endif

%files soap -f files.soap

%files bcmath -f files.bcmath
%doc libbcmath_COPYING

%files gmp -f files.gmp

%files dba -f files.dba

%files pdo -f files.pdo

%files mcrypt -f files.mcrypt

%files tidy -f files.tidy

%files mssql -f files.mssql

%files pspell -f files.pspell

%files intl -f files.intl

%files process -f files.process

%files recode -f files.recode

%files interbase -f files.interbase

%files enchant -f files.enchant

%files mysqlnd -f files.mysqlnd

%files opcache -f files.opcache
%config(noreplace) %{_sysconfdir}/php.d/opcache-default.blacklist
%config(noreplace) %{_sysconfdir}/php-zts.d/opcache-default.blacklist

%changelog
* Tue Feb 11 2014 Remi Collet <remi@fedoraproject.org> 5.5.9-1
- Update to 5.5.9
  http://www.php.net/ChangeLog-5.php#5.5.9
- Install macros to /usr/lib/rpm/macros.d

* Thu Jan 23 2014 Joe Orton <jorton@redhat.com> - 5.5.8-2
- fix _httpd_mmn expansion in absence of httpd-devel

* Wed Jan  8 2014 Remi Collet <rcollet@redhat.com> 5.5.8-1
- update to 5.5.8
- drop conflicts with other opcode caches as both can
  be used only for user data cache

* Wed Dec 11 2013 Remi Collet <rcollet@redhat.com> 5.5.7-1
- update to 5.5.7, fix for CVE-2013-6420
- fix zend_register_functions breaks reflection, php bug 66218
- fix Heap buffer over-read in DateInterval, php bug 66060
- fix fix overflow handling bug in non-x86

* Wed Nov 13 2013 Remi Collet <remi@fedoraproject.org> 5.5.6-1
- update to 5.5.6

* Thu Oct 17 2013 Remi Collet <rcollet@redhat.com> - 5.5.5-1
- update to 5.5.5
- sync php.ini with upstream

* Thu Sep 19 2013 Remi Collet <rcollet@redhat.com> - 5.5.4-1
- update to 5.5.4
- improve security, use specific soap.wsdl_cache_dir
  use /var/lib/php/wsdlcache for mod_php and php-fpm
- sync short_tag comments in php.ini with upstream

* Wed Aug 21 2013 Remi Collet <rcollet@redhat.com> - 5.5.3-1
- update to 5.5.3
- fix typo and add missing entries in php.ini
- drop zip extension

* Mon Aug 19 2013 Remi Collet <rcollet@redhat.com> - 5.5.2-1
- update to 5.5.2, fixes for CVE-2011-4718 + CVE-2013-4248

* Thu Aug 08 2013 Remi Collet <rcollet@redhat.com> - 5.5.1-3
- improve system libzip patch

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 22 2013 Remi Collet <rcollet@redhat.com> - 5.5.1-1
- update to 5.5.1
- add Provides: php(pdo-abi), for consistency with php(api)
  and php(zend-abi)
- improved description for mod_php
- fix opcache ZTS configuration (blacklists in /etc/php-zts.d)
- add missing man pages (phar, php-cgi)

* Fri Jul 12 2013 Remi Collet <rcollet@redhat.com> - 5.5.0-2
- add security fix for CVE-2013-4113
- add missing ASL 1.0 license
- 32k stack size seems ok for tests on both 32/64bits build

* Thu Jun 20 2013 Remi Collet <rcollet@redhat.com> 5.5.0-1
- update to 5.5.0 final

* Fri Jun 14 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.11.RC3
- also drop JSON from sources
- clean conditional for JSON (as removed from the sources)
- clean conditional for FPM (always build)

* Thu Jun 13 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.10.RC3
- drop JSON extension

* Tue Jun 11 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.9.RC3
- build with system GD >= 2.1.0

* Thu Jun  6 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.8.RC3
- update to 5.5.0RC3

* Thu May 23 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.7.RC2
- update to 5.5.0RC2
- add missing options in php-fpm.conf
- run php-fpm in systemd notify mode
- /etc/syconfig/php-fpm is deprecated (still used)
- add /systemd/system/php-fpm.service.d

* Wed May  8 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.6.RC1
- update to 5.5.0RC1
- remove reference to apache in some sub-packages description
- add option to disable json extension
- drop most (very old) "Obsoletes", add version to others

* Thu Apr 25 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.5.beta4
- update to 5.5.0beta4
- zend_extension doesn't requires full path
- refresh patch for system libzip
- drop opcache patch merged upstream
- add BuildRequires libvpx-devel for WebP support in php-gd
- php-fpm own /usr/share/fpm

* Thu Apr 11 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.4.beta3
- update to 5.5.0beta3
- allow wildcard in opcache.blacklist_filename and provide
  default /etc/php.d/opcache-default.blacklist
- clean spec, use only spaces (no tab)

* Thu Apr  4 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.3.beta2
- clean old deprecated options

* Thu Mar 28 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.2.beta2
- update to 5.5.0beta2
- Zend Optimizer+ renamed to Zend OPcache
- sync provided configuration with upstream

* Fri Mar 22 2013 Remi Collet <rcollet@redhat.com> 5.5.0-0.1.beta1
- update to 5.5.0beta1
  http://fedoraproject.org/wiki/Features/Php55
- new Zend OPcache extension in php-opccache new sub-package
- don't display XFAIL tests in report
- use xz compressed tarball
- build simplexml and xml extensions shared (moved in php-xml)
- build bz2, calendar, ctype, exif, ftp, gettext, iconv
  sockets and tokenizer extensions shared (in php-common)
- build gmp extension shared (in php-gmp new sub-package)
- build shmop extension shared (moved in php-process)
- drop some old compatibility provides (php-api, php-zend-abi, php-pecl-*)

* Thu Mar 14 2013 Remi Collet <rcollet@redhat.com> 5.4.13-1
- update to 5.4.13
- security fix for CVE-2013-1643
- Hardened build (links with -z now option)

* Mon Mar 11 2013 Ralf Corsépius <corsepiu@fedoraproject.org> -  5.4.13-0.2.RC1
- Remove %%config from %%{_sysconfdir}/rpm/macros.*
  (https://fedorahosted.org/fpc/ticket/259).

* Thu Feb 28 2013 Remi Collet <rcollet@redhat.com> 5.4.13-0.1.RC1
- update to 5.4.13RC1
- drop patches merged upstream

* Sat Feb 23 2013 Karsten Hopp <karsten@redhat.com> 5.4.12-4
- add support for ppc64p7 arch (Power7 optimized)

* Thu Feb 21 2013 Remi Collet <rcollet@redhat.com> 5.4.12-3
- make ZTS build optional (still enabled)

* Wed Feb 20 2013 Remi Collet <rcollet@redhat.com> 5.4.12-2
- make php-mysql package optional and disabled

* Wed Feb 20 2013 Remi Collet <remi@fedoraproject.org> 5.4.12-1
- update to 5.4.12
- security fix for CVE-2013-1635
- drop gdbm because of license incompatibility

* Wed Feb 13 2013 Remi Collet <rcollet@redhat.com> 5.4.12-0.6.RC2
- enable tokyocabinet and gdbm dba handlers

* Wed Feb 13 2013 Remi Collet <rcollet@redhat.com> 5.4.12-0.5.RC2
- update to 5.4.12RC2

* Mon Feb 11 2013 Remi Collet <rcollet@redhat.com> 5.4.12-0.4.RC1
- upstream patch (5.4.13) to fix dval to lval conversion
  https://bugs.php.net/64142

* Mon Feb  4 2013 Remi Collet <rcollet@redhat.com> 5.4.12-0.3.RC1
- upstream patch (5.4.13) for 2 failed tests

* Fri Feb  1 2013 Remi Collet <rcollet@redhat.com> 5.4.12-0.2.RC1
- fix buit-in web server on ppc64 (fdset usage)
  https://bugs.php.net/64128

* Thu Jan 31 2013 Remi Collet <rcollet@redhat.com> 5.4.12-0.1.RC1
- update to 5.4.12RC1

* Mon Jan 28 2013 Remi Collet <rcollet@redhat.com> 5.4.11-3
- rebuild for new libicu

* Mon Jan 21 2013 Adam Tkac <atkac redhat com> - 5.4.11-2
- rebuild due to "jpeg8-ABI" feature drop

* Wed Jan 16 2013 Remi Collet <rcollet@redhat.com> 5.4.11-1
- update to 5.4.11

* Thu Jan 10 2013 Remi Collet <rcollet@redhat.com> 5.4.11-0.2.RC1
- fix php.conf to allow MultiViews managed by php scripts

* Thu Jan 10 2013 Remi Collet <rcollet@redhat.com> 5.4.11-0.1.RC1
- update to 5.4.11RC1

* Wed Dec 19 2012 Remi Collet <rcollet@redhat.com> 5.4.10-1
- update to 5.4.10
- remove patches merged upstream

* Tue Dec 11 2012 Remi Collet <rcollet@redhat.com> 5.4.9-3
- drop "Configure Command" from phpinfo output

* Tue Dec 11 2012 Joe Orton <jorton@redhat.com> - 5.4.9-2
- prevent php_config.h changes across (otherwise identical) rebuilds

* Thu Nov 22 2012 Remi Collet <rcollet@redhat.com> 5.4.9-1
- update to 5.4.9

* Thu Nov 15 2012 Remi Collet <rcollet@redhat.com> 5.4.9-0.5.RC1
- switch back to upstream generated scanner/parser

* Thu Nov 15 2012 Remi Collet <rcollet@redhat.com> 5.4.9-0.4.RC1
- use _httpd_contentdir macro and fix php.gif path

* Wed Nov 14 2012 Remi Collet <rcollet@redhat.com> 5.4.9-0.3.RC1
- improve system libzip patch to use pkg-config

* Wed Nov 14 2012 Remi Collet <rcollet@redhat.com> 5.4.9-0.2.RC1
- use _httpd_moddir macro

* Wed Nov 14 2012 Remi Collet <rcollet@redhat.com> 5.4.9-0.1.RC1
- update to 5.4.9RC1
- improves php.conf (use FilesMatch + SetHandler)
- improves filter (httpd module)
- apply ldap_r patch on fedora >= 18 only

* Fri Nov  9 2012 Remi Collet <rcollet@redhat.com> 5.4.8-6
- clarify Licenses
- missing provides xmlreader and xmlwriter
- modernize spec
- change php embedded library soname version to 5.4

* Tue Nov  6 2012 Remi Collet <rcollet@redhat.com> 5.4.8-5
- fix _httpd_mmn macro definition

* Mon Nov  5 2012 Remi Collet <rcollet@redhat.com> 5.4.8-4
- fix mysql_sock macro definition

* Thu Oct 25 2012 Remi Collet <rcollet@redhat.com> 5.4.8-3
- fix installed headers

* Tue Oct 23 2012 Joe Orton <jorton@redhat.com> - 5.4.8-2
- use libldap_r for ldap extension

* Thu Oct 18 2012 Remi Collet <remi@fedoraproject.org> 5.4.8-1
- update to 5.4.8
- define both session.save_handler and session.save_path
- fix possible segfault in libxml (#828526)
- php-fpm: create apache user if needed
- use SKIP_ONLINE_TEST during make test
- php-devel requires pcre-devel and php-cli (instead of php)

* Fri Oct  5 2012 Remi Collet <remi@fedoraproject.org> 5.4.7-11
- provides php-phar
- update systzdata patch to v10, timezone are case insensitive

* Mon Oct  1 2012 Remi Collet <remi@fedoraproject.org> 5.4.7-10
- fix typo in systemd macro

* Mon Oct  1 2012 Remi Collet <remi@fedoraproject.org> 5.4.7-9
- php-fpm: enable PrivateTmp
- php-fpm: new systemd macros (#850268)
- php-fpm: add upstream patch for startup issue (#846858)

* Fri Sep 28 2012 Remi Collet <rcollet@redhat.com> 5.4.7-8
- systemd integration, https://bugs.php.net/63085
- no odbc call during timeout, https://bugs.php.net/63171
- check sqlite3_column_table_name, https://bugs.php.net/63149

* Mon Sep 24 2012 Remi Collet <rcollet@redhat.com> 5.4.7-7
- most failed tests explained (i386, x86_64)

* Wed Sep 19 2012 Remi Collet <rcollet@redhat.com> 5.4.7-6
- fix for http://bugs.php.net/63126 (#783967)

* Wed Sep 19 2012 Remi Collet <rcollet@redhat.com> 5.4.7-5
- patch to ensure we use latest libdb (not libdb4)

* Wed Sep 19 2012 Remi Collet <rcollet@redhat.com> 5.4.7-4
- really fix rhel tests (use libzip and libdb)

* Tue Sep 18 2012 Remi Collet <rcollet@redhat.com> 5.4.7-3
- fix test to enable zip extension on RHEL-7

* Mon Sep 17 2012 Remi Collet <remi@fedoraproject.org> 5.4.7-2
- remove session.save_path from php.ini
  move it to apache and php-fpm configuration files

* Fri Sep 14 2012 Remi Collet <remi@fedoraproject.org> 5.4.7-1
- update to 5.4.7
  http://www.php.net/releases/5_4_7.php
- php-fpm: don't daemonize

* Mon Aug 20 2012 Remi Collet <remi@fedoraproject.org> 5.4.6-2
- enable php-fpm on secondary arch (#849490)

* Fri Aug 17 2012 Remi Collet <remi@fedoraproject.org> 5.4.6-1
- update to 5.4.6
- update to v9 of systzdata patch
- backport fix for new libxml

* Fri Jul 20 2012 Remi Collet <remi@fedoraproject.org> 5.4.5-1
- update to 5.4.5

* Mon Jul 02 2012 Remi Collet <remi@fedoraproject.org> 5.4.4-4
- also provide php(language)%%{_isa}
- define %%{php_version}

* Mon Jul 02 2012 Remi Collet <remi@fedoraproject.org> 5.4.4-3
- drop BR for libevent (#835671)
- provide php(language) to allow version check

* Thu Jun 21 2012 Remi Collet <remi@fedoraproject.org> 5.4.4-2
- add missing provides (core, ereg, filter, standard)

* Thu Jun 14 2012 Remi Collet <remi@fedoraproject.org> 5.4.4-1
- update to 5.4.4 (CVE-2012-2143, CVE-2012-2386)
- use /usr/lib/tmpfiles.d instead of /etc/tmpfiles.d
- use /run/php-fpm instead of /var/run/php-fpm

* Wed May 09 2012 Remi Collet <remi@fedoraproject.org> 5.4.3-1
- update to 5.4.3 (CVE-2012-2311, CVE-2012-2329)

* Thu May 03 2012 Remi Collet <remi@fedoraproject.org> 5.4.2-1
- update to 5.4.2 (CVE-2012-1823)

* Fri Apr 27 2012 Remi Collet <remi@fedoraproject.org> 5.4.1-1
- update to 5.4.1

* Wed Apr 25 2012 Joe Orton <jorton@redhat.com> - 5.4.0-6
- rebuild for new icu
- switch (conditionally) to libdb-devel

* Sat Mar 31 2012 Remi Collet <remi@fedoraproject.org> 5.4.0-5
- fix Loadmodule with MPM event (use ZTS if not MPM worker)
- split conf.d/php.conf + conf.modules.d/10-php.conf with httpd 2.4

* Thu Mar 29 2012 Joe Orton <jorton@redhat.com> - 5.4.0-4
- rebuild for missing automatic provides (#807889)

* Mon Mar 26 2012 Joe Orton <jorton@redhat.com> - 5.4.0-3
- really use _httpd_mmn

* Mon Mar 26 2012 Joe Orton <jorton@redhat.com> - 5.4.0-2
- rebuild against httpd 2.4
- use _httpd_mmn, _httpd_apxs macros

* Fri Mar 02 2012 Remi Collet <remi@fedoraproject.org> 5.4.0-1
- update to PHP 5.4.0 finale

* Sat Feb 18 2012 Remi Collet <remi@fedoraproject.org> 5.4.0-0.4.RC8
- update to PHP 5.4.0RC8

* Sat Feb 04 2012 Remi Collet <remi@fedoraproject.org> 5.4.0-0.3.RC7
- update to PHP 5.4.0RC7
- provides env file for php-fpm (#784770)
- add patch to use system libzip (thanks to spot)
- don't provide INSTALL file

* Wed Jan 25 2012 Remi Collet <remi@fedoraproject.org> 5.4.0-0.2.RC6
- all binaries in /usr/bin with zts prefix

* Wed Jan 18 2012 Remi Collet <remi@fedoraproject.org> 5.4.0-0.1.RC6
- update to PHP 5.4.0RC6
  https://fedoraproject.org/wiki/Features/Php54

* Sun Jan 08 2012 Remi Collet <remi@fedoraproject.org> 5.3.8-4.4
- fix systemd unit

* Mon Dec 12 2011 Remi Collet <remi@fedoraproject.org> 5.3.8-4.3
- switch to systemd

* Tue Dec 06 2011 Adam Jackson <ajax@redhat.com> - 5.3.8-4.2
- Rebuild for new libpng

* Wed Oct 26 2011 Marcela Mašláňová <mmaslano@redhat.com> - 5.3.8-3.2
- rebuild with new gmp without compat lib

* Wed Oct 12 2011 Peter Schiffer <pschiffe@redhat.com> - 5.3.8-3.1
- rebuild with new gmp

* Wed Sep 28 2011 Remi Collet <remi@fedoraproject.org> 5.3.8-3
- revert is_a() to php <= 5.3.6 behavior (from upstream)
  with new option (allow_string) for new behavior

* Tue Sep 13 2011 Remi Collet <remi@fedoraproject.org> 5.3.8-2
- add mysqlnd sub-package
- drop patch4, use --libdir to use /usr/lib*/php/build
- add patch to redirect mysql.sock (in mysqlnd)

* Tue Aug 23 2011 Remi Collet <remi@fedoraproject.org> 5.3.8-1
- update to 5.3.8
  http://www.php.net/ChangeLog-5.php#5.3.8

* Thu Aug 18 2011 Remi Collet <remi@fedoraproject.org> 5.3.7-1
- update to 5.3.7
  http://www.php.net/ChangeLog-5.php#5.3.7
- merge php-zts into php (#698084)

* Tue Jul 12 2011 Joe Orton <jorton@redhat.com> - 5.3.6-4
- rebuild for net-snmp SONAME bump

* Mon Apr  4 2011 Remi Collet <Fedora@famillecollet.com> 5.3.6-3
- enable mhash extension (emulated by hash extension)

* Wed Mar 23 2011 Remi Collet <Fedora@famillecollet.com> 5.3.6-2
- rebuild for new MySQL client library

* Thu Mar 17 2011 Remi Collet <Fedora@famillecollet.com> 5.3.6-1
- update to 5.3.6
  http://www.php.net/ChangeLog-5.php#5.3.6
- fix php-pdo arch specific requires

* Tue Mar 15 2011 Joe Orton <jorton@redhat.com> - 5.3.5-6
- disable zip extension per "No Bundled Libraries" policy (#551513)

* Mon Mar 07 2011 Caolán McNamara <caolanm@redhat.com> 5.3.5-5
- rebuild for icu 4.6

* Mon Feb 28 2011 Remi Collet <Fedora@famillecollet.com> 5.3.5-4
- fix systemd-units requires

* Thu Feb 24 2011 Remi Collet <Fedora@famillecollet.com> 5.3.5-3
- add tmpfiles.d configuration for php-fpm
- add Arch specific requires/provides

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan 07 2011 Remi Collet <Fedora@famillecollet.com> 5.3.5-1
- update to 5.3.5
  http://www.php.net/ChangeLog-5.php#5.3.5
- clean duplicate configure options

* Tue Dec 28 2010 Remi Collet <rpms@famillecollet.com> 5.3.4-2
- rebuild against MySQL 5.5.8
- remove all RPM_SOURCE_DIR

* Sun Dec 12 2010 Remi Collet <rpms@famillecollet.com> 5.3.4-1.1
- security patch from upstream for #660517

* Sat Dec 11 2010 Remi Collet <Fedora@famillecollet.com> 5.3.4-1
- update to 5.3.4
  http://www.php.net/ChangeLog-5.php#5.3.4
- move phpize to php-cli (see #657812)

* Wed Dec  1 2010 Remi Collet <Fedora@famillecollet.com> 5.3.3-5
- ghost /var/run/php-fpm (see #656660)
- add filter_setup to not provides extensions as .so

* Mon Nov  1 2010 Joe Orton <jorton@redhat.com> - 5.3.3-4
- use mysql_config in libdir directly to avoid biarch build failures

* Fri Oct 29 2010 Joe Orton <jorton@redhat.com> - 5.3.3-3
- rebuild for new net-snmp

* Sun Oct 10 2010 Remi Collet <Fedora@famillecollet.com> 5.3.3-2
- add php-fpm sub-package

* Thu Jul 22 2010 Remi Collet <Fedora@famillecollet.com> 5.3.3-1
- PHP 5.3.3 released

* Fri Apr 30 2010 Remi Collet <Fedora@famillecollet.com> 5.3.2-3
- garbage collector upstream  patches (#580236)

* Fri Apr 02 2010 Caolán McNamara <caolanm@redhat.com> 5.3.2-2
- rebuild for icu 4.4

* Sat Mar 06 2010 Remi Collet <Fedora@famillecollet.com> 5.3.2-1
- PHP 5.3.2 Released!
- remove mime_magic option (now provided by fileinfo, by emu)
- add patch for http://bugs.php.net/50578
- remove patch for libedit (upstream)
- add runselftest option to allow build without test suite

* Fri Nov 27 2009 Joe Orton <jorton@redhat.com> - 5.3.1-3
- update to v7 of systzdata patch

* Wed Nov 25 2009 Joe Orton <jorton@redhat.com> - 5.3.1-2
- fix build with autoconf 2.6x

* Fri Nov 20 2009 Remi Collet <Fedora@famillecollet.com> 5.3.1-1
- update to 5.3.1
- remove openssl patch (merged upstream)
- add provides for php-pecl-json
- add prod/devel php.ini in doc

* Tue Nov 17 2009 Tom "spot" Callaway <tcallawa@redhat.com> - 5.3.0-7
- use libedit instead of readline to resolve licensing issues

* Tue Aug 25 2009 Tomas Mraz <tmraz@redhat.com> - 5.3.0-6
- rebuilt with new openssl

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 16 2009 Joe Orton <jorton@redhat.com> 5.3.0-4
- rediff systzdata patch

* Thu Jul 16 2009 Joe Orton <jorton@redhat.com> 5.3.0-3
- update to v6 of systzdata patch; various fixes

* Tue Jul 14 2009 Joe Orton <jorton@redhat.com> 5.3.0-2
- update to v5 of systzdata patch; parses zone.tab and extracts
  timezone->{country-code,long/lat,comment} mapping table

* Sun Jul 12 2009 Remi Collet <Fedora@famillecollet.com> 5.3.0-1
- update to 5.3.0
- remove ncurses, dbase, mhash extensions
- add enchant, sqlite3, intl, phar, fileinfo extensions
- raise sqlite version to 3.6.0 (for sqlite3, build with --enable-load-extension)
- sync with upstream "production" php.ini

* Sun Jun 21 2009 Remi Collet <Fedora@famillecollet.com> 5.2.10-1
- update to 5.2.10
- add interbase sub-package

* Sat Feb 28 2009 Remi Collet <Fedora@FamilleCollet.com> - 5.2.9-1
- update to 5.2.9

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.2.8-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Feb  5 2009 Joe Orton <jorton@redhat.com> 5.2.8-9
- add recode support, -recode subpackage (#106755)
- add -zts subpackage with ZTS-enabled build of httpd SAPI
- adjust php.conf to use -zts SAPI build for worker MPM

* Wed Feb  4 2009 Joe Orton <jorton@redhat.com> 5.2.8-8
- fix patch fuzz, renumber patches

* Wed Feb  4 2009 Joe Orton <jorton@redhat.com> 5.2.8-7
- drop obsolete configure args
- drop -odbc patch (#483690)

* Mon Jan 26 2009 Joe Orton <jorton@redhat.com> 5.2.8-5
- split out sysvshm, sysvsem, sysvmsg, posix into php-process

* Sun Jan 25 2009 Joe Orton <jorton@redhat.com> 5.2.8-4
- move wddx to php-xml, build curl shared in -common
- remove BR for expat-devel, bogus configure option

* Fri Jan 23 2009 Joe Orton <jorton@redhat.com> 5.2.8-3
- rebuild for new MySQL

* Sat Dec 13 2008 Remi Collet <Fedora@FamilleCollet.com> 5.2.8-2
- libtool 2 workaround for phpize (#476004)
- add missing php_embed.h (#457777)

* Tue Dec 09 2008 Remi Collet <Fedora@FamilleCollet.com> 5.2.8-1
- update to 5.2.8

* Sat Dec 06 2008 Remi Collet <Fedora@FamilleCollet.com> 5.2.7-1.1
- libtool 2 workaround

* Fri Dec 05 2008 Remi Collet <Fedora@FamilleCollet.com> 5.2.7-1
- update to 5.2.7
- enable pdo_dblib driver in php-mssql

* Mon Nov 24 2008 Joe Orton <jorton@redhat.com> 5.2.6-7
- tweak Summary, thanks to Richard Hughes

* Tue Nov  4 2008 Joe Orton <jorton@redhat.com> 5.2.6-6
- move gd_README to php-gd
- update to r4 of systzdata patch; introduces a default timezone
  name of "System/Localtime", which uses /etc/localtime (#469532)

* Sat Sep 13 2008 Remi Collet <Fedora@FamilleCollet.com> 5.2.6-5
- enable XPM support in php-gd
- Fix BR for php-gd

* Sun Jul 20 2008 Remi Collet <Fedora@FamilleCollet.com> 5.2.6-4
- enable T1lib support in php-gd

* Mon Jul 14 2008 Joe Orton <jorton@redhat.com> 5.2.6-3
- update to 5.2.6
- sync default php.ini with upstream
- drop extension_dir from default php.ini, rely on hard-coded
  default, to make php-common multilib-safe (#455091)
- update to r3 of systzdata patch

* Thu Apr 24 2008 Joe Orton <jorton@redhat.com> 5.2.5-7
- split pspell extension out into php-spell (#443857)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 5.2.5-6
- Autorebuild for GCC 4.3

* Fri Jan 11 2008 Joe Orton <jorton@redhat.com> 5.2.5-5
- ext/date: use system timezone database

* Fri Dec 28 2007 Joe Orton <jorton@redhat.com> 5.2.5-4
- rebuild for libc-client bump

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 5.2.5-3
- Rebuild for openssl bump

* Wed Dec  5 2007 Joe Orton <jorton@redhat.com> 5.2.5-2
- update to 5.2.5

* Mon Oct 15 2007 Joe Orton <jorton@redhat.com> 5.2.4-3
- correct pcre BR version (#333021)
- restore metaphone fix (#205714)
- add READMEs to php-cli

* Sun Sep 16 2007 Joe Orton <jorton@redhat.com> 5.2.4-2
- update to 5.2.4

* Sun Sep  2 2007 Joe Orton <jorton@redhat.com> 5.2.3-9
- rebuild for fixed APR

* Tue Aug 28 2007 Joe Orton <jorton@redhat.com> 5.2.3-8
- add ldconfig post/postun for -embedded (Hans de Goede)

* Fri Aug 10 2007 Hans de Goede <j.w.r.degoede@hhs.nl> 5.2.3-7
- add php-embedded sub-package

* Fri Aug 10 2007 Joe Orton <jorton@redhat.com> 5.2.3-6
- fix build with new glibc
- fix License

* Mon Jul 16 2007 Joe Orton <jorton@redhat.com> 5.2.3-5
- define php_extdir in macros.php

* Mon Jul  2 2007 Joe Orton <jorton@redhat.com> 5.2.3-4
- obsolete php-dbase

* Tue Jun 19 2007 Joe Orton <jorton@redhat.com> 5.2.3-3
- add mcrypt, mhash, tidy, mssql subpackages (Dmitry Butskoy)
- enable dbase extension and package in -common

* Fri Jun  8 2007 Joe Orton <jorton@redhat.com> 5.2.3-2
- update to 5.2.3 (thanks to Jeff Sheltren)

* Wed May  9 2007 Joe Orton <jorton@redhat.com> 5.2.2-4
- fix php-pdo *_arg_force_ref global symbol abuse (#216125)

* Tue May  8 2007 Joe Orton <jorton@redhat.com> 5.2.2-3
- rebuild against uw-imap-devel

* Fri May  4 2007 Joe Orton <jorton@redhat.com> 5.2.2-2
- update to 5.2.2
- synch changes from upstream recommended php.ini

* Thu Mar 29 2007 Joe Orton <jorton@redhat.com> 5.2.1-5
- enable SASL support in LDAP extension (#205772)

* Wed Mar 21 2007 Joe Orton <jorton@redhat.com> 5.2.1-4
- drop mime_magic extension (deprecated by php-pecl-Fileinfo)

* Mon Feb 19 2007 Joe Orton <jorton@redhat.com> 5.2.1-3
- fix regression in str_{i,}replace (from upstream)

* Thu Feb 15 2007 Joe Orton <jorton@redhat.com> 5.2.1-2
- update to 5.2.1
- add Requires(pre) for httpd
- trim %%changelog to versions >= 5.0.0

* Thu Feb  8 2007 Joe Orton <jorton@redhat.com> 5.2.0-10
- bump default memory_limit to 32M (#220821)
- mark config files noreplace again (#174251)
- drop trailing dots from Summary fields
- use standard BuildRoot
- drop libtool15 patch (#226294)

* Tue Jan 30 2007 Joe Orton <jorton@redhat.com> 5.2.0-9
- add php(api), php(zend-abi) provides (#221302)
- package /usr/share/php and append to default include_path (#225434)

* Tue Dec  5 2006 Joe Orton <jorton@redhat.com> 5.2.0-8
- fix filter.h installation path
- fix php-zend-abi version (Remi Collet, #212804)

* Tue Nov 28 2006 Joe Orton <jorton@redhat.com> 5.2.0-7
- rebuild again

* Tue Nov 28 2006 Joe Orton <jorton@redhat.com> 5.2.0-6
- rebuild for net-snmp soname bump

* Mon Nov 27 2006 Joe Orton <jorton@redhat.com> 5.2.0-5
- build json and zip shared, in -common (Remi Collet, #215966)
- obsolete php-json and php-pecl-zip
- build readline extension into /usr/bin/php* (#210585)
- change module subpackages to require php-common not php (#177821)

* Wed Nov 15 2006 Joe Orton <jorton@redhat.com> 5.2.0-4
- provide php-zend-abi (#212804)
- add /etc/rpm/macros.php exporting interface versions
- synch with upstream recommended php.ini

* Wed Nov 15 2006 Joe Orton <jorton@redhat.com> 5.2.0-3
- update to 5.2.0 (#213837)
- php-xml provides php-domxml (#215656)
- fix php-pdo-abi provide (#214281)

* Tue Oct 31 2006 Joseph Orton <jorton@redhat.com> 5.1.6-4
- rebuild for curl soname bump
- add build fix for curl 7.16 API

* Wed Oct  4 2006 Joe Orton <jorton@redhat.com> 5.1.6-3
- from upstream: add safety checks against integer overflow in _ecalloc

* Tue Aug 29 2006 Joe Orton <jorton@redhat.com> 5.1.6-2
- update to 5.1.6 (security fixes)
- bump default memory_limit to 16M (#196802)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 5.1.4-8.1
- rebuild

* Fri Jun  9 2006 Joe Orton <jorton@redhat.com> 5.1.4-8
- Provide php-posix (#194583)
- only provide php-pcntl from -cli subpackage
- add missing defattr's (thanks to Matthias Saou)

* Fri Jun  9 2006 Joe Orton <jorton@redhat.com> 5.1.4-7
- move Obsoletes for php-openssl to -common (#194501)
- Provide: php-cgi from -cli subpackage

* Fri Jun  2 2006 Joe Orton <jorton@redhat.com> 5.1.4-6
- split out php-cli, php-common subpackages (#177821)
- add php-pdo-abi version export (#193202)

* Wed May 24 2006 Radek Vokal <rvokal@redhat.com> 5.1.4-5.1
- rebuilt for new libnetsnmp

* Thu May 18 2006 Joe Orton <jorton@redhat.com> 5.1.4-5
- provide mod_php (#187891)
- provide php-cli (#192196)
- use correct LDAP fix (#181518)
- define _GNU_SOURCE in php_config.h and leave it defined
- drop (circular) dependency on php-pear

* Mon May  8 2006 Joe Orton <jorton@redhat.com> 5.1.4-3
- update to 5.1.4

* Wed May  3 2006 Joe Orton <jorton@redhat.com> 5.1.3-3
- update to 5.1.3

* Tue Feb 28 2006 Joe Orton <jorton@redhat.com> 5.1.2-5
- provide php-api (#183227)
- add provides for all builtin modules (Tim Jackson, #173804)
- own %%{_libdir}/php/pear for PEAR packages (per #176733)
- add obsoletes to allow upgrade from FE4 PDO packages (#181863)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 5.1.2-4.3
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 5.1.2-4.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 31 2006 Joe Orton <jorton@redhat.com> 5.1.2-4
- rebuild for new libc-client soname

* Mon Jan 16 2006 Joe Orton <jorton@redhat.com> 5.1.2-3
- only build xmlreader and xmlwriter shared (#177810)

* Fri Jan 13 2006 Joe Orton <jorton@redhat.com> 5.1.2-2
- update to 5.1.2

* Thu Jan  5 2006 Joe Orton <jorton@redhat.com> 5.1.1-8
- rebuild again

* Mon Jan  2 2006 Joe Orton <jorton@redhat.com> 5.1.1-7
- rebuild for new net-snmp

* Mon Dec 12 2005 Joe Orton <jorton@redhat.com> 5.1.1-6
- enable short_open_tag in default php.ini again (#175381)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Dec  8 2005 Joe Orton <jorton@redhat.com> 5.1.1-5
- require net-snmp for php-snmp (#174800)

* Sun Dec  4 2005 Joe Orton <jorton@redhat.com> 5.1.1-4
- add /usr/share/pear back to hard-coded include_path (#174885)

* Fri Dec  2 2005 Joe Orton <jorton@redhat.com> 5.1.1-3
- rebuild for httpd 2.2

* Mon Nov 28 2005 Joe Orton <jorton@redhat.com> 5.1.1-2
- update to 5.1.1
- remove pear subpackage
- enable pdo extensions (php-pdo subpackage)
- remove non-standard conditional module builds
- enable xmlreader extension

* Thu Nov 10 2005 Tomas Mraz <tmraz@redhat.com> 5.0.5-6
- rebuilt against new openssl

* Mon Nov  7 2005 Joe Orton <jorton@redhat.com> 5.0.5-5
- pear: update to XML_RPC 1.4.4, XML_Parser 1.2.7, Mail 1.1.9 (#172528)

* Tue Nov  1 2005 Joe Orton <jorton@redhat.com> 5.0.5-4
- rebuild for new libnetsnmp

* Wed Sep 14 2005 Joe Orton <jorton@redhat.com> 5.0.5-3
- update to 5.0.5
- add fix for upstream #34435
- devel: require autoconf, automake (#159283)
- pear: update to HTTP-1.3.6, Mail-1.1.8, Net_SMTP-1.2.7, XML_RPC-1.4.1
- fix imagettftext et al (upstream, #161001)

* Thu Jun 16 2005 Joe Orton <jorton@redhat.com> 5.0.4-11
- ldap: restore ldap_start_tls() function

* Fri May  6 2005 Joe Orton <jorton@redhat.com> 5.0.4-10
- disable RPATHs in shared extensions (#156974)

* Tue May  3 2005 Joe Orton <jorton@redhat.com> 5.0.4-9
- build simplexml_import_dom even with shared dom (#156434)
- prevent truncation of copied files to ~2Mb (#155916)
- install /usr/bin/php from CLI build alongside CGI
- enable sysvmsg extension (#142988)

* Mon Apr 25 2005 Joe Orton <jorton@redhat.com> 5.0.4-8
- prevent build of builtin dba as well as shared extension

* Wed Apr 13 2005 Joe Orton <jorton@redhat.com> 5.0.4-7
- split out dba and bcmath extensions into subpackages
- BuildRequire gcc-c++ to avoid AC_PROG_CXX{,CPP} failure (#155221)
- pear: update to DB-1.7.6
- enable FastCGI support in /usr/bin/php-cgi (#149596)

* Wed Apr 13 2005 Joe Orton <jorton@redhat.com> 5.0.4-6
- build /usr/bin/php with the CLI SAPI, and add /usr/bin/php-cgi,
  built with the CGI SAPI (thanks to Edward Rudd, #137704)
- add php(1) man page for CLI
- fix more test cases to use -n when invoking php

* Wed Apr 13 2005 Joe Orton <jorton@redhat.com> 5.0.4-5
- rebuild for new libpq soname

* Tue Apr 12 2005 Joe Orton <jorton@redhat.com> 5.0.4-4
- bundle from PEAR: HTTP, Mail, XML_Parser, Net_Socket, Net_SMTP
- snmp: disable MSHUTDOWN function to prevent error_log noise (#153988)
- mysqli: add fix for crash on x86_64 (Georg Richter, upstream #32282)

* Mon Apr 11 2005 Joe Orton <jorton@redhat.com> 5.0.4-3
- build shared objects as PIC (#154195)

* Mon Apr  4 2005 Joe Orton <jorton@redhat.com> 5.0.4-2
- fix PEAR installation and bundle PEAR DB-1.7.5 package

* Fri Apr  1 2005 Joe Orton <jorton@redhat.com> 5.0.4-1
- update to 5.0.4 (#153068)
- add .phps AddType to php.conf (#152973)
- better gcc4 fix for libxmlrpc

* Wed Mar 30 2005 Joe Orton <jorton@redhat.com> 5.0.3-5
- BuildRequire mysql-devel >= 4.1
- don't mark php.ini as noreplace to make upgrades work (#152171)
- fix subpackage descriptions (#152628)
- fix memset(,,0) in Zend (thanks to Dave Jones)
- fix various compiler warnings in Zend

* Thu Mar 24 2005 Joe Orton <jorton@redhat.com> 5.0.3-4
- package mysqli extension in php-mysql
- really enable pcntl (#142903)
- don't build with --enable-safe-mode (#148969)
- use "Instant Client" libraries for oci8 module (Kai Bolay, #149873)

* Fri Feb 18 2005 Joe Orton <jorton@redhat.com> 5.0.3-3
- fix build with GCC 4

* Wed Feb  9 2005 Joe Orton <jorton@redhat.com> 5.0.3-2
- install the ext/gd headers (#145891)
- enable pcntl extension in /usr/bin/php (#142903)
- add libmbfl array arithmetic fix (dcb314@hotmail.com, #143795)
- add BuildRequire for recent pcre-devel (#147448)

* Wed Jan 12 2005 Joe Orton <jorton@redhat.com> 5.0.3-1
- update to 5.0.3 (thanks to Robert Scheck et al, #143101)
- enable xsl extension (#142174)
- package both the xsl and dom extensions in php-xml
- enable soap extension, shared (php-soap package) (#142901)
- add patches from upstream 5.0 branch:
 * Zend_strtod.c compile fixes
 * correct php_sprintf return value usage

* Mon Nov 22 2004 Joe Orton <jorton@redhat.com> 5.0.2-8
- update for db4-4.3 (Robert Scheck, #140167)
- build against mysql-devel
- run tests in %%check

* Wed Nov 10 2004 Joe Orton <jorton@redhat.com> 5.0.2-7
- truncate changelog at 4.3.1-1
- merge from 4.3.x package:
 - enable mime_magic extension and Require: file (#130276)

* Mon Nov  8 2004 Joe Orton <jorton@redhat.com> 5.0.2-6
- fix dom/sqlite enable/without confusion

* Mon Nov  8 2004 Joe Orton <jorton@redhat.com> 5.0.2-5
- fix phpize installation for lib64 platforms
- add fix for segfault in variable parsing introduced in 5.0.2

* Mon Nov  8 2004 Joe Orton <jorton@redhat.com> 5.0.2-4
- update to 5.0.2 (#127980)
- build against mysqlclient10-devel
- use new RTLD_DEEPBIND to load extension modules
- drop explicit requirement for elfutils-devel
- use AddHandler in default conf.d/php.conf (#135664)
- "fix" round() fudging for recent gcc on x86
- disable sqlite pending audit of warnings and subpackage split

* Fri Sep 17 2004 Joe Orton <jorton@redhat.com> 5.0.1-4
- don't build dom extension into 2.0 SAPI

* Fri Sep 17 2004 Joe Orton <jorton@redhat.com> 5.0.1-3
- ExclusiveArch: x86 ppc x86_64 for the moment

* Fri Sep 17 2004 Joe Orton <jorton@redhat.com> 5.0.1-2
- fix default extension_dir and conf.d/php.conf

* Thu Sep  9 2004 Joe Orton <jorton@redhat.com> 5.0.1-1
- update to 5.0.1
- only build shared modules once
- put dom extension in php-dom subpackage again
- move extension modules into %%{_libdir}/php/modules
- don't use --with-regex=system, it's ignored for the apache* SAPIs

* Wed Aug 11 2004 Tom Callaway <tcallawa@redhat.com>
- Merge in some spec file changes from Jeff Stern (jastern@uci.edu)

* Mon Aug 09 2004 Tom Callaway <tcallawa@redhat.com>
- bump to 5.0.0
- add patch to prevent clobbering struct re_registers from regex.h
- remove domxml references, replaced with dom now built-in
- fix php.ini to refer to php5 not php4
