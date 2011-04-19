from setuptools import setup

setup(
    name='rapidsms-status160',
    version='0.1',
    license="BSD",

    # install_requires = ["rapidsms",
    #                 'django-eav',
    #                 'rapidsms-auth',
    #                 'rapidsms-polls',
    #                 'simple_locations'
    #     ],
    # 
    #     dependency_links = [
    #         "http://github.com/mvpdev/django-eav/tarball/master#egg=django-eav",
    #         "http://github.com/daveycrockett/auth/tarball/master#egg=rapidsms-auth",
    #         "http://github.com/daveycrockett/rapidsms-polls/tarball/master#egg=rapidsms-polls",
    #         "http://github.com/mossplix/simple_location/tarball/master#egg=simple_locations",
    #     ],

	install_requires = [
        "rapidsms",
        'rapidsms-xforms',
        'rapidsms-auth',
        'rapidsms-polls',
        'rapidsms-httprouter',
        'rapidsms-ureport',
        'django-extensions',
        'django-uni-form',
        'django-eav',
        'simple_locations',
        'rapidsms-auth',
        'rapidsms-authsites',
    ],
    
    dependency_links = [
        "http://github.com/daveycrockett/rapidsms-xforms/tarball/master#egg=rapidsms-xforms",
        "http://github.com/mossplix/simple_locations/tarball/master#egg=simple_locations",
        "http://github.com/daveycrockett/auth/tarball/master#egg=rapidsms-auth",
        "http://github.com/daveycrockett/rapidsms-polls/tarball/master#egg=rapidsms-polls",
        "http://github.com/daveycrockett/rapidsms-httprouter/tarball/master#egg=rapidsms-httprouter",
        "http://github.com/daveycrockett/rapidsms-ureport/tarball/master#egg=rapidsms-ureport",
        "http://github.com/mvpdev/django-eav/tarball/master#egg=django-eav",
        "http://github.com/daveycrockett/auth/tarball/master#egg=rapidsms-auth",
        "http://github.com/daveycrockett/rapidsms-authsites/tarball/master#egg=rapidsms-authsites",
    ],

    description='An application for managing emergency situations, allowing admins to send out security surveys and assess a crisis situation.',
    long_description=open('README.rst').read(),
    author='David McCann',
    author_email='david.a.mccann@gmail.com',

    url='http://github.com:daveycrockett/rapidsms-status160',
    download_url='http://github.com:daveycrockett/rapidsms-status160/downloads',

    include_package_data=True,

    packages=['status160'],

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
