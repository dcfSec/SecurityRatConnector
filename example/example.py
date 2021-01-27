from securityratconnector import securityratconnector

# Initialise connector
connector = securityratconnector.SecurityRatConnector('http://server/api')

# Login to the api
connector.doLogin('user', 'password')

# getCollectionCategories
# @TODO: Why does this call needs to be done before i can use a post request?
connector.getCollectionCategories()

# addCollectionCategory
addedCollectionCategory = connector.addCollectionCategory('Test', 'This is a test category')

# getCollectionCategories
gotCollectionCategory = connector.getCollectionCategory(addedCollectionCategory['id'])

# updateCollectionCategory
updatedCollectionCategory = connector.updateCollectionCategory(addedCollectionCategory['id'], name='Test change',
                                                               description='This is a test change category')

# addCollectionInstance
addedCollectionInstance = connector.addCollectionInstance('Test', 'This is a test instance',
                                                          addedCollectionCategory['id'])

# getCollectionInstance
connector.getCollectionInstance(addedCollectionInstance['id'])

# updateCollectionInstance
updatedCollectionInstance = connector.updateCollectionInstance(addedCollectionInstance['id'], name='Test change',
                                                               description='This is a test change instance')

# getCollectionInstances
connector.getCollectionInstances()

# addTagCategory
addedTagCategory = connector.addTagCategory('Test', 'This is a tag category')

# getTagCategory
connector.getTagCategory(addedTagCategory['id'])

# updateTagCategory
updatedTagCategory = connector.updateTagCategory(addedTagCategory['id'], name='Test change',
                                                 description='This is a test change tag category')

# getTagCategories
connector.getTagCategories()

# addTagInstance
addedTagInstance = connector.addTagInstance('Test', 'This is a tag Instance', addedTagCategory['id'])

# getTagInstance
connector.getTagInstance(addedTagInstance['id'])

# updateTagInstance
updatedTagInstance = connector.updateTagInstance(addedTagInstance['id'], name='Test change',
                                                 description='This is a test change tag Instance')

# getTagInstances
connector.getTagInstances()

# addRequirementCategory
addedRequirementCategory = connector.addRequirementCategory('Test', 'ST', 'This is a Requirement category')

# getRequirementCategory
connector.getRequirementCategory(addedRequirementCategory['id'])

# updateRequirementCategory
updatedRequirementCategory = connector.updateRequirementCategory(addedRequirementCategory['id'], name='Test change',
                                                                 description='This is a test change Requirement category')

# getRequirementCategories
connector.getRequirementCategories()

# addRequirementSkeleton
addedRequirementSkeleton = connector.addRequirementSkeleton('TSK', 'This is a tag Instance',
                                                            addedRequirementCategory['id'],
                                                            [addedCollectionInstance['id']], [addedTagInstance['id']])

# getRequirementSkeleton
connector.getRequirementSkeleton(addedRequirementSkeleton['id'])

# updateRequirementSkeleton
updatedRequirementSkeleton = connector.updateRequirementSkeleton(addedRequirementSkeleton['id'],
                                                                 description='This is a test change tag Instance',
                                                                 tagInstances=[])

# getRequirementSkeletons
connector.getRequirementSkeletons()

# addOptColumnType
addedOptColumnType = connector.addOptColumnType('Test', 'This is a optColumn type')

# getOptColumnType
connector.getOptColumnType(addedOptColumnType['id'])

# updateOptColumnType
updatedOptColumnType = connector.updateOptColumnType(addedOptColumnType['id'], name='Test change',
                                                     description='This is a test change optColumn type')

# getOptColumnType
connector.getOptColumnTypes()

# addOptColumn
addedOptColumn = connector.addOptColumn('Test', 'This is a test instance', addedOptColumnType['id'])

# getOptColumn
connector.getOptColumn(addedOptColumn['id'])

# updateOptColumn
updatedOptColumn = connector.updateOptColumn(addedOptColumn['id'], name='Test change',
                                             description='This is a test change instance')

# getOptColumns
connector.getOptColumns()

# addOptColumnContent
addedOptColumnContent = connector.addOptColumnContent('This is a test instance', addedOptColumn['id'],
                                                      addedRequirementSkeleton['id'])

# getOptColumnContent
connector.getOptColumnContent(addedOptColumnContent['id'])

# updateOptColumnContent
updatedOptColumnContent = connector.updateOptColumnContent(addedOptColumnContent['id'], content='Test change content')

# getOptColumnContents
connector.getOptColumnContents()

# deleteOptColumnContent
connector.deleteOptColumnContent(addedOptColumnContent['id'])

# deleteOptColumn
connector.deleteOptColumn(addedOptColumn['id'])

# deleteOptColumnType
connector.deleteOptColumnType(addedOptColumnType['id'])

# deleteRequirementSkeleton
connector.deleteRequirementSkeleton(addedRequirementSkeleton['id'])

# deleteRequirementCategory
connector.deleteRequirementCategory(addedRequirementCategory['id'])

# deleteTagInstance
connector.deleteTagInstance(addedTagInstance['id'])

# deleteTagCategory
connector.deleteTagCategory(addedTagCategory['id'])

# deleteCollectionInstance
connector.deleteCollectionInstance(addedCollectionInstance['id'])

# deleteCollectionCategory
connector.deleteCollectionCategory(addedCollectionCategory['id'])
