Changes
=======

1.0a3 (2022-10-06)
------------------

- Replace deprecated use of ``IStorage`` by ``IMappingStorage``.
  [rnix]

- Replace deprecated use of ``Storage`` by ``MappingStorage``.
  [rnix]

- Replace deprecated use of ``Nodify`` by ``MappingNode``.
  [rnix]

- Replace deprecated use of ``NodeChildValidate`` by ``MappingConstraints``.
  [rnix]


1.0a2 (2021-10-21)
------------------

- Implement ``node.iterfaces.IOrder`` on ``ZODBEntry``.
  [rnix]


1.0a1 (2020-07-09)
------------------

- Fix case where ``_v_parent`` is not set if ``ZODBEntryNode`` is not read via
  ``ZODBEntryStorage`` but from ZODB root directly.
  [rnix]

- Remove ``AsAttrAccess``, ``Nodespaces``, and ``Attributes`` behaviors from
  ``ZODBEntry``.
  [rnix]

- Add ``ZODBEntryStorage.attrs``. Returns attributes of related
  ``ZODBEntryNode``.
  [rnix]

- Add ``ZODBEntryNode.__getitem__``. Sets ``ZODBEntryNode.entry`` as parent
  on children to keep traversal and acquisition paths sane.
  [rnix]

- Access ``principal_roles`` when initializing nodes with ``ZODBPrincipalACL``
  behavior applied to avoid lazy creation. Needed to prevent ``_p_changed``
  being set on first access.
  [rnix]

- Do not remember ``principal_roles`` via ``instance_property`` decorator
  on ``ZODBEntryPrincipalACL`` to avoid ``ZODB.POSException.ConnectionStateError``
  errors.
  [rnix]

- Proper handling of ``ZODBEntry`` and ``ZODBEntryNode`` in ``zodb_path``.
  [rnix]

- Add ``include_entry`` attribute to ``CatalogAware`` behavior. Flag controls
  whether to index entry node in calatog.
  [rnix]

- Add ``entry`` property to ``ZODBEntryNode``.
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
