.. _intro:

Introduction
============

What is lang-gamification-api?
------------------------------

This is a project to explore the benefit of using gamification in language learning. It provides a back-end API, and a website served via Flask. Mobile apps are coming soon too.

Installation instructions
-------------------------

Requirements
^^^^^^^^^^^^

::

	Flask==0.10.1
	Jinja2==2.8
	pymongo==3.0.3
	Sphinx==1.3.1
	Werkzeug==0.10.4
	uwsgi==2.0.11.2
	nose==1.3.7
	passlib==1.6.5
	cloud_sptheme==1.7

The app should be wrapped with something like uWSGI or gnunicorn, and then would also need ``nginx``, and ``MongoDB``.

Install
^^^^^^^

A complete install guide available :ref:`here <complete-install>`.