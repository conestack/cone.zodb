
Changes
=======


1.0a1 (unreleased)
------------------

- Access ``principal_roles`` when initializing nodes with ``ZODBPrincipalACL``
  behavior applied to avoid lazy creation. Needed to prevent ``_p_changed``
  being set by ZODB on first access.
  [rnix]

- Set ``_v_parent`` instead of ``__parent__`` in ``ZODBEntryStorage.storage``
  to prevent ``_p_changed`` being set by ZODB on access.
  [rnix]

- Do not remember ``principal_roles`` via ``instance_property`` decorator
  on ``ZODBEntryPrincipalACL`` to avoid ``ZODB.POSException.ConnectionStateError``
  errors.
  [rnix]

- Proper handling of ``ZODBEntry`` in ``zodb_path``.
  [rnix]

- Add ``include_entry`` attribute to ``CatalogAware`` behavior. Flag controls
  whether to index entry node in calatog.
  [rnix]

- Add ``entry`` property to ``ZODBEntryNode``.
  [rnix]

- Add ``__parent__`` setter function to ``ZODBEntryNode``.
  [rnix]

- Use ``pyramid_zodbconn`` instead of ``repoze.zodbconn``.
  [rnix]

- Set ``node.interfaces.IOrdered`` on ``cone.zodb.entry.ZODBEntry`` to fix
  ``treerepr``.
  [rnix]

- Python 3 compatibility.
  [rnix]

- Upgrade to ``cone.app`` 1.0b1.
  [rnix]


< 1.0
-----

- Initial work.
  [rnix]
