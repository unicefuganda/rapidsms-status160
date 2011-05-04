from setuptools import setup

setup(
    name='rapidsms-status160',
    version='0.1',
    license="BSD",

	install_requires = [
        "rapidsms",
        'django-extensions',
        'django-uni-form',
        'rapidsms-auth',
        'rapidsms-polls',
        'rapidsms-httprouter',
        'django-eav',
        'simple-locations',
        'rapidsms-contact',
		'rapidsms-generic',
        'rapidsms-ureport',
        'uganda-common',
    ],
    
    dependency_links = [
        "http://github.com/mossplix/simple_locations/tarball/master#egg=simple-locations",
        "http://github.com/daveycrockett/auth/tarball/master#egg=rapidsms-auth",
        "http://github.com/daveycrockett/rapidsms-polls/tarball/master#egg=rapidsms-polls",
        "http://github.com/daveycrockett/rapidsms-httprouter/tarball/master#egg=rapidsms-httprouter",
        "http://github.com/mvpdev/django-eav/tarball/master#egg=django-eav",
		"http://github.com/mossplix/rapidsms-contact/tarball/master#egg=rapidsms-contact",
        "http://github.com/daveycrockett/rapidsms-generic/tarball/master#egg=rapidsms-generic",
        "http://github.com/daveycrockett/rapidsms-ureport/tarball/master#egg=rapidsms-ureport",
        "http://github.com/mossplix/uganda_common/tarball/master#egg=uganda-common",
    ],

    description='An application for managing emergency situations, allowing admins to send out security surveys and assess a crisis situation.',
    long_description=open('README.rst').read(),
    author='David McCann',
    author_email='david.a.mccann@gmail.com',

    url='http://github.com/daveycrockett/rapidsms-status160',
    download_url='http://github.com/daveycrockett/rapidsms-status160/downloads',

    include_package_data=True,

    packages=['status160'],
    package_data={'status160':['templates/*/*.html','templates/*/*/*.html','static/*/*']},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
