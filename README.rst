Getbook
=======

Chinese websites parsers for getbook_.

.. _getbook: https://github.com/lepture/getbook

.. image:: https://img.shields.io/badge/donate-lepture-ff69b4.svg
   :target: https://lepture.com/donate
   :alt: Donate lepture

Installation
------------

Install with uv::

    $ uv add getbook-chinese

Or with pip::

    $ pip install getbook-chinese

Usage
-----

Pass the book's index page URL to ``getbook`` with the ``-u`` flag.

Create EPUB book::

    $ uv run getbook -u https://www.kanunu8.com/book6/xajianghu/

Create MOBI book::

    $ uv run getbook --mobi -u https://www.kanunu8.com/book6/xajianghu/

The tool will fetch the chapter list from the index page and download
each chapter automatically, then package them into the chosen format.
