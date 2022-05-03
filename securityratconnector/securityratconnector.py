"""
This module provides a connector to SecurityRat
"""
import requests
from collections import UserList, UserDict
from typing import List, Union


# @ToDo: add find to all entries
# @ToDo: better exception handling for rest calls


class SecurityRatConnector:
    """
    SecurityRatConnector is a python class to access the SecurityRat API via REST.
    If cached is True all get requests will be cached to prevent unnecessary requests to the server.
    A changing request overrides the cache at the next get

    :param str apiEndpoint: API endpoint of SecurityRat. This is the full base URL like http://example.com/api
    :param bool verifyCertificates: If False certificate validation is deactivated for the requests, default is True
    :param bool cached: If enabled all get requests will be cached, default is True
    """

    def __init__(self, apiEndpoint: str, verifyCertificates: bool = True, cached: bool = True):
        """
        Initializes the class with the API endpoint and caching options.
        """
        self.session = requests.session()
        self.api = apiEndpoint
        self.verifyCertificates = verifyCertificates
        self.cached = cached
        self.cache = {}
        self.headers = {'content-type': 'application/json;charset=utf-8', 'Accept': 'application/json',
                        'X-CSRF-TOKEN': None}

    def getRawSession(self) -> requests.session:
        """
        Returns the used requests session. Might be useful if session parameters need to be changed.

        :return requests.session: The used requests session
        """
        return self.session

    def getCached(self, cacheId: str) -> Union[list, dict]:
        """
        If caching is activated the cached version will be returned if it is unchanged.

        :param str cacheId: The ID of the cache (Also the API call name)
        :return list,dict: Returns the API data
        """
        if self.cached is True:
            if cacheId in self.cache.keys() and self.cache[cacheId] is not None:
                return self.cache[cacheId]
            else:
                self.cache[cacheId] = self.get(cacheId)
                return self.cache[cacheId]
        else:
            return self.get(cacheId)

    def getConfig(self) -> None:
        """
        Request to the API endpoint to retrieve some base information for the session.

        :raises Exception: Raises an exception if the request is unsuccessfully
        """
        config = self.session.get(self.api + '/authentication_config', headers={'content-type': 'application/json'},
                                  verify=self.verifyCertificates)
        if config.status_code != 200:
            raise Exception('Login unsuccessfully: Code: %s\nMessage: %s' % (config.status_code, config.content))

    def login(self, user: str, password: str) -> bool:
        """
        Sends the login request to the API endpoint to retrieve a valid session.

        :param str user: The user name of the used account
        :param str password: The password of the used account
        :return bool: Returns True if the login was successful
        :raises Exception: Raises an exception if the login is unsuccessfully
        """
        login = self.session.post(self.api + '/authentication', params={'j_password': password, 'j_username': user},
                                  headers={'Content-Type': 'application/x-www-form-urlencoded',
                                           'Accept': 'application/json',
                                           'X-CSRF-TOKEN': self.session.cookies['CSRF-TOKEN']},
                                  verify=self.verifyCertificates)
        if login.status_code != 200:
            raise Exception('Login unsuccessfully: Code: %s\nMessage: %s' % (login.status_code, login.content))
        return True

    def doLogin(self, user: str, password: str) -> bool:
        """
        Does the whole login process with getting the configuration and doing the actual login.

        :param str user: The user name of the used account
        :param str password: The password of the used account
        :return bool: Returns True if the login was successful
        """
        self.getConfig()
        return self.login(user, password)

    def put(self, endpoint: str, data: dict) -> dict:
        """
        Uses the PUT call to update data in the API

        :param str endpoint: The API endpoint which needs to be called e.g. collectionInstances
        :param dict data: The data which will be sent
        :return dict: The answer from the server
        :raises Exception: Raises an exception if the request is unsuccessfully
        """
        self.headers['X-CSRF-TOKEN'] = self.session.cookies['CSRF-TOKEN']
        req = self.session.put(self.api + '/' + endpoint, json=data, headers=self.headers,
                               verify=self.verifyCertificates)
        if req.status_code >= 400:
            raise Exception('Request unsuccessfully: %s' % req.status_code)

        if self.cached is True and endpoint in self.cache.keys():
            self.cache[endpoint] = None
        return req.json()

    def get(self, endpoint: str) -> Union[list, dict]:
        """
        Uses the GET call to retrieve data from the server

        :param str endpoint: The API endpoint which needs to be called e.g. collectionInstances
        :return dict: The answer from the server
        :raises Exception: Raises an exception if the request is unsuccessfully
        """
        self.headers['X-CSRF-TOKEN'] = self.session.cookies['CSRF-TOKEN']
        req = self.session.get(self.api + '/' + endpoint, headers=self.headers, verify=self.verifyCertificates)
        if req.status_code >= 400:
            raise Exception('Request unsuccessfully: %s' % req.status_code)
        return req.json()

    def delete(self, endpoint: str) -> bool:
        """
        Uses the DELETE call to delete data from the server

        :param str endpoint: The API endpoint which needs to be called e.g. collectionInstances
        :return dict: The answer from the server
        :raises Exception: Raises an exception if the request is unsuccessfully
        """
        self.headers['X-CSRF-TOKEN'] = self.session.cookies['CSRF-TOKEN']
        req = self.session.delete(self.api + '/' + endpoint, headers=self.headers, verify=self.verifyCertificates)
        if req.status_code >= 400:
            raise Exception('Request unsuccessfully: %s' % req.status_code)
        if self.cached is True and endpoint in self.cache.keys():
            self.cache[endpoint] = None
        return True

    def post(self, endpoint: str, data: dict) -> dict:
        """
        Uses the POST call to add data to the server

        :param str endpoint: The API endpoint which needs to be called e.g. collectionInstances
        :param dict data: The data which will be sent
        :return dict: The answer from the server
        :raises Exception: Raises an exception if the request is unsuccessfully
        """
        headers = {'content-type': 'application/json;charset=utf-8', 'Accept': 'application/json',
                   'X-CSRF-TOKEN': self.session.cookies['CSRF-TOKEN']}
        req = self.session.post(self.api + '/' + endpoint, json=data, headers=headers, verify=self.verifyCertificates)
        if req.status_code >= 400:
            raise Exception('Request unsuccessfully: %s' % req.content)
        if self.cached is True and endpoint in self.cache.keys():
            self.cache[endpoint] = None
        return req.json()

    def getCollectionCategory(self, id_) -> dict:
        """
        Returns a specific collection category

        :param int id_: The Id of the object The Id of the object
        :return dict: The requested data
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none. Use getCollectionCategories for a list of all collection categories')
        return self.get('collectionCategorys/%s' % id_)

    def getCollectionCategories(self) -> list:
        """
        Returns all collection categories

        :return dict: The requested data
        """
        return self.getCached('collectionCategorys')

    def addCollectionCategory(self, name: str, description: str, showOrder: int = 0, active: bool = False) -> dict:
        """
        Adds a collection category

        :param str name: The name of the object
        :param str description: The description of the object
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The answer from the server
        """
        data = {
            'name': name,
            'description': description,
            'showOrder': showOrder,
            'active': active,
            'id': None
        }
        return self.post('collectionCategorys', data)

    def updateCollectionCategory(self, id_: int, name: str = None, description: str = None, showOrder: int = None,
                                 active: bool = None) -> dict:
        """
        Updates a specific collection category. A entry is unchanged if the parameter is None

        :param int id_: The Id of the object
        :param str name: The name of the object
        :param str description: The description of the object
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        data = self.getCollectionCategory(id_)
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if showOrder is not None:
            data['showOrder'] = showOrder
        if active is not None:
            data['active'] = active
        return self.put('collectionCategorys', data)

    def deleteCollectionCategory(self, id_: int) -> bool:
        """
        Deletes a specific collection category

        :param int id_: The Id of the object
        :return bool: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.delete('collectionCategorys/%s' % id_)

    def getCollectionInstance(self, id_: int) -> dict:
        """
        Returns a selected collection instance

        :param int id_: The Id of the object
        :return dict: Selected collection instance
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.get('collectionInstances/%s' % id_)

    def getCollectionInstances(self) -> list:
        """
        Returns all collection instances

        :return list: A list of all collection instances
        """
        return self.getCached('collectionInstances')

    def addCollectionInstance(self, name: str, description: str, collectionCategoryId: int, showOrder: int = 0,
                              active: bool = False) -> dict:
        """
        Adds a new collection instance

        :param str name: The name of the object
        :param str description: The description of the object
        :param int collectionCategoryId: Id of the mapped collection category
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The answer from the server
        """
        data = {
            'name': name,
            'description': description,
            'showOrder': showOrder,
            'active': active,
            'id': None,
            'collectionCategory': {
                'id': collectionCategoryId,
            }
        }
        return self.post('collectionInstances', data)

    def updateCollectionInstance(self, id_: int, name: str = None, description: str = None,
                                 collectionCategoryId: int = None, showOrder: int = None, active: bool = None) -> dict:
        """
        Updates an existing collection instance

        :param int id_: The Id of the object
        :param str name: The name of the object
        :param str description: The description of the object
        :param int collectionCategoryId: Id of the mapped collection category
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The answer from the server
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        data = self.getCollectionInstance(id_)
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if showOrder is not None:
            data['showOrder'] = showOrder
        if active is not None:
            data['active'] = active
        if collectionCategoryId is not None:
            data['collectionCategory'] = {'id': collectionCategoryId}
        return self.put('collectionInstances', data)

    def deleteCollectionInstance(self, id_):
        """
        Deletes a specific collection instance

        :param int id_: The Id of the object
        :return bool: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.delete('collectionInstances/%s' % id_)

    def getTagCategory(self, id_: int) -> dict:
        """
        Gets a specific tag category

        :param int id_: The Id of the object
        :return dict: The selected tag category
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.get('tagCategorys/%s' % id_)

    def getTagCategories(self) -> list:
        """
        Gets all tag categories

        :return list: all tag categories
        """
        return self.getCached('tagCategorys')

    def addTagCategory(self, name: str, description: str, showOrder: int = 0, active: bool = False) -> dict:
        """
        Adds a new tag category

        :param str name: The name of the object
        :param str description: The description of the object
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The answer from the server
        """
        data = {
            'name': name,
            'description': description,
            'showOrder': showOrder,
            'active': active,
            'id': None
        }
        return self.post('tagCategorys', data)

    def updateTagCategory(self, id_: int, name: str = None, description: str = None, showOrder: int = None,
                          active: bool = None) -> dict:
        """
        Updates a tag category

        :param int id_: The Id of the object
        :param str name: The name of the object
        :param str description: The description of the object
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        data = self.getTagCategory(id_)
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if showOrder is not None:
            data['showOrder'] = showOrder
        if active is not None:
            data['active'] = active
        return self.put('tagCategorys', data)

    def deleteTagCategory(self, id_: int) -> bool:
        """
        Deletes a tag category

        :param int id_: The Id of the object
        :return bool: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.delete('tagCategorys/%s' % id_)

    def getTagInstance(self, id_: int) -> dict:
        """
        Gets a tag instance from the server

        :param int id_: The Id of the object
        :return dict: The requested tag instance
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.get('tagInstances/%s' % id_)

    def getTagInstances(self) -> list:
        """
        Gets all tag instances

        :return list: all tag categories
        """
        return self.getCached('tagInstances')

    def addTagInstance(self, name: str, description: str, tagCategoryId: int, showOrder: int = 0,
                       active: bool = False) -> dict:
        """
        Adds a tag instance

        :param str name: The name of the object
        :param str description: The description of the object
        :param int tagCategoryId: The tag category of this instance
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The answer from the server
        """
        data = {
            'name': name,
            'description': description,
            'showOrder': showOrder,
            'active': active,
            'id': None,
            'tagCategory': {
                'id': tagCategoryId
            }
        }
        return self.post('tagInstances', data)

    def updateTagInstance(self, id_: int, name: str = None, description: str = None, tagCategoryId: int = None,
                          showOrder: int = None, active: bool = None) -> dict:
        """
        Updates a tag instance

        :param int id_: The Id of the object
        :param str name: The name of the object
        :param str description: The description of the object
        :param int tagCategoryId: The tag category of this instance
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        data = self.getTagInstance(id_)
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if showOrder is not None:
            data['showOrder'] = showOrder
        if active is not None:
            data['active'] = active
        if tagCategoryId is not None:
            data['tagCategory'] = {'id': tagCategoryId}
        return self.put('tagInstances', data)

    def deleteTagInstance(self, id_: int) -> bool:
        """
        Deletes a tag instance

        :param int id_: The Id of the object
        :return bool: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.delete('tagInstances/%s' % id_)

    def getRequirementCategory(self, id_: int) -> dict:
        """
        Gets a requirement category from the server

        :param int id_: The Id of the object
        :return dict: The requested requirement category
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.get('reqCategorys/%s' % id_)

    def getRequirementCategories(self) -> list:
        """
        Gets all requirement categories

        :return list: all requirement categories
        """
        return self.getCached('reqCategorys')

    def addRequirementCategory(self, name: str, shortcut: str, description: str, showOrder: int = 0,
                               active: bool = False) -> dict:
        """
        Adds a requirement category to the server

        :param str name: The name of the object
        :param str shortcut: Short name of this category
        :param str description: The description of the object
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The answer from the server
        """
        data = {
            'name': name,
            'shortcut': shortcut,
            'description': description,
            'showOrder': showOrder,
            'active': active,
            'id': None
        }
        return self.post('reqCategorys', data)

    def updateRequirementCategory(self, id_: int, name: str = None, shortcut: str = None, description: str = None,
                                  showOrder: int = None, active: bool = None) -> dict:
        """
        Updates a requirement category

        :param int id_: The Id of the object
        :param str name: The name of the object
        :param str shortcut: Short name of this category
        :param str description: The description of the object
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        data = self.getRequirementCategory(id_)
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if showOrder is not None:
            data['showOrder'] = showOrder
        if active is not None:
            data['active'] = active
        if shortcut is not None:
            data['shortcut'] = shortcut
        return self.put('reqCategorys', data)

    def deleteRequirementCategory(self, id_: int) -> bool:
        """
        Deletes a requirement category

        :param int id_: The Id of the object
        :return bool: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.delete('reqCategorys/%s' % id_)

    def getRequirementSkeleton(self, id_: int) -> dict:
        """
        Gets a requirement skeleton from the server

        :param int id_: The Id of the object
        :return dict: The requested requirement skeleton
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.get('requirementSkeletons/%s' % id_)

    def getRequirementSkeletons(self) -> list:
        """
        Gets all requirement skeletons

        :return list: all requirement skeletons
        """
        return self.getCached('requirementSkeletons')

    # noinspection DuplicatedCode
    def addRequirementSkeleton(self, shortName: str, description: str, requirementCategory: int,
                               collectionInstances: list = None, tagInstances: list = None, projectTypes: list = None,
                               showOrder: int = 0, active: bool = False, universalId: str = None) -> dict:
        """
        Adds a requirement skeleton to the server

        :param str shortName: A short name for this skeleton
        :param str description: The description of the object
        :param int requirementCategory: the mapped requirement category
        :param list collectionInstances: A list of mapped collection instances
        :param list tagInstances: A list of mapped tag instances
        :param list projectTypes: A list of mapped project types
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :param str universalId: A universal ID
        :return dict: The answer from the server
        """
        if projectTypes is None:
            projectTypes = []
        if tagInstances is None:
            tagInstances = []
        if collectionInstances is None:
            collectionInstances = []
        collectionInstancesDataList = []
        tagInstancesDataList = []
        projectTypesDataList = []

        for i in collectionInstances:
            collectionInstancesDataList.append({'id': i})
        for i in tagInstances:
            tagInstancesDataList.append({'id': i})
        for i in projectTypes:
            projectTypesDataList.append({'id': i})

        data = {
            'shortName': shortName,
            'description': description,
            'showOrder': showOrder,
            'active': active,
            'id': None,
            'universalId': universalId,
            'reqCategory': {'id': requirementCategory},
            'tagInstances': tagInstancesDataList,
            'collectionInstances': collectionInstancesDataList,
            'projectTypes': projectTypesDataList,
        }
        return self.post('requirementSkeletons', data)

    def updateRequirementSkeleton(self, id_: int, shortName: str = None, description: str = None,
                                  requirementCategory: int = None, collectionInstances: list = None,
                                  tagInstances: list = None, projectTypes: list = None, showOrder: int = None,
                                  active: bool = None, universalId: str = None) -> dict:
        """
        Updates a requirement skeleton

        :param int id_: The Id of the object
        :param str shortName: A short name for this skeleton
        :param str description: The description of the object
        :param int requirementCategory: the mapped requirement category
        :param list collectionInstances: A list of mapped collection instances
        :param list tagInstances: A list of mapped tag instances
        :param list projectTypes: A list of mapped project types
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :param str universalId: A universal ID
        :return dict: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        data = self.getRequirementSkeleton(id_)
        if description is not None:
            data['description'] = description
        if showOrder is not None:
            data['showOrder'] = showOrder
        if active is not None:
            data['active'] = active
        if shortName is not None:
            data['shortName'] = shortName
        if requirementCategory is not None:
            data['reqCategory'] = {'id': requirementCategory}
        if collectionInstances is not None:
            collectionInstancesDataList = []
            for i in collectionInstances:
                collectionInstancesDataList.append({'id': i})
            data['collectionInstances'] = collectionInstancesDataList
        if tagInstances is not None:
            tagInstancesDataList = []
            for i in tagInstances:
                tagInstancesDataList.append({'id': i})
            data['tagInstances'] = tagInstancesDataList
        if projectTypes is not None:
            projectTypesDataList = []
            for i in projectTypes:
                projectTypesDataList.append({'id': i})
            data['projectTypes'] = projectTypesDataList
        if universalId is not None:
            data['universalId'] = universalId
        return self.put('requirementSkeletons', data)

    def findRequirementSkeletonWithProjectType(self, projectType: Union[list, int]) -> list:
        """
        Returns a list of requirement skeletons which have a given project type

        :param list,int projectType: A list or a single project type
        :return list: Found skeletons
        """
        data = self.getRequirementSkeletons()
        found = []
        if not isinstance(projectType, list):
            projectTypeList = [projectType]
        else:
            projectTypeList = projectType
        for v in data:
            for v1 in v['projectTypes']:
                if v1['id'] in projectTypeList:
                    found.append(v)
        return found

    def deleteRequirementSkeleton(self, id_: int) -> bool:
        """
        Deletes a requirement skeleton

        :param int id_: The Id of the object
        :return bool: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.delete('requirementSkeletons/%s' % id_)

    def getOptColumnType(self, id_: int) -> dict:
        """
        Gets an optional column type from the server

        :param int id_: The Id of the object
        :return dict: The requested optional column type
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.get('optColumnTypes/%s' % id_)

    def getOptColumnTypes(self):
        """
        Gets all optional column types

        :return list: all optional column types
        """
        return self.getCached('optColumnTypes')

    def addOptColumnType(self, name: str, description: str) -> dict:
        """
        Adds a new optional column type

        :param str name: The name of the object
        :param str description: The description of the object
        :return dict: The answer from the server
        """
        data = {
            'name': name,
            'description': description,
            'id': None
        }
        return self.post('optColumnTypes', data)

    def updateOptColumnType(self, id_: int, name: str = None, description: str = None) -> dict:
        """
        Updates an optional column type

        :param int id_: The Id of the object
        :param str name: The name of the object
        :param str description: The description of the object
        :return dict: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        data = self.getOptColumnType(id_)
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        return self.put('optColumnTypes', data)

    def deleteOptColumnType(self, id_: int) -> bool:
        """
        Deletes an optional column type

        :param int id_: The Id of the object
        :return bool: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.delete('optColumnTypes/%s' % id_)

    def getOptColumn(self, id_: int) -> dict:
        """
        Gets an optional column from the server

        :param int id_: The Id of the object
        :return dict: The requested optional column
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.get('optColumns/%s' % id_)

    def getOptColumns(self) -> list:
        """
        Gets all optional column

        :return list: all optional column
        """
        return self.getCached('optColumns')

    def addOptColumn(self, name: str, description: str, optColumnTypeId: int, showOrder: int = 0, active: bool = False,
                     isVisibleByDefault: bool = True) -> dict:
        """
        Adds a optional column ti the server

        :param str name: The name of the object
        :param str description: The description of the object
        :param int optColumnTypeId: The mapped optional column type id
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :param bool isVisibleByDefault: Sets if it is visible by default
        :return dict: The requested optional column
        """
        data = {
            'name': name,
            'description': description,
            'showOrder': showOrder,
            'active': active,
            'isVisibleByDefault': isVisibleByDefault,
            'id': None,
            'optColumnType': {
                'id': optColumnTypeId,
            }
        }
        return self.post('optColumns', data)

    def updateOptColumn(self, id_: int, name: str = None, description: str = None, optColumnTypeId: int = None,
                        showOrder: int = None, active: bool = None, isVisibleByDefault: bool = None) -> dict:
        """
        Updates an optional column

        :param int id_: The Id of the object
        :param str name: The name of the object
        :param str description: The description of the object
        :param int optColumnTypeId: The mapped optional column type id
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :param bool isVisibleByDefault: Sets if it is visible by default
        :return dict: The requested optional column
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        data = self.getOptColumn(id_)
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if showOrder is not None:
            data['showOrder'] = showOrder
        if active is not None:
            data['active'] = active
        if optColumnTypeId is not None:
            data['optColumnType'] = {'id': optColumnTypeId}
        if isVisibleByDefault is not None:
            data['isVisibleByDefault'] = isVisibleByDefault
        return self.put('optColumns', data)

    def deleteOptColumn(self, id_: int) -> bool:
        """

        Deletes an optional column

        :param int id_: The Id of the object
        :return bool: The answer from the server
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.delete('optColumns/%s' % id_)

    def getOptColumnContent(self, id_: int) -> dict:
        """
        Gets an optional column content from the server

        :param int id_: The Id of the object
        :return dict: The requested optional column content
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.get('optColumnContents/%s' % id_)

    def getOptColumnContents(self) -> list:
        """
        Gets all optional column contents

        :return list: all optional column contents
        """
        return self.getCached('optColumnContents')

    def findOptColumnContentsWithRequirementSkeletonId(self, requirementSkeletonId: int) -> list:
        """
        Gets a list of optional column contents with a specific requirement skeleton id

        :param int requirementSkeletonId: the mapped requirement skeleton id
        :return list: list of found items
        """
        data = self.getOptColumnContents()
        found = []
        for v in data:
            if v['requirementSkeleton']['id'] == requirementSkeletonId:
                found.append(v)
        return found

    def findOptColumnContentsWithOptColumnId(self, optColumnId: int) -> list:  # @ToDo: Combine search?
        """
        Gets a list of optional column contents with a specific optional column id

        :param int optColumnId: the mapped optional column id
        :return list: list of found items
        """
        data = self.getOptColumnContents()
        found = []
        for v in data:
            if v['optColumn']['id'] == optColumnId:
                found.append(v)
        return found

    def findOptColumnContentsWithContent(self, search: str, regex: bool = False) -> list:
        """
        Gets a list of optional column contents with a specific string in them

        :param str search: The search string
        :param bool regex: Enables a regex search (Not implemented at the moment)
        :return list: list of found items
        :ToDo: Implement regex search
        """
        data = self.getOptColumnContents()
        found = []
        for v in data:
            if v['content'].find(search) != -1:
                found.append(v)
        return found

    def addOptColumnContent(self, content: str, optColumnId: int, requirementSkeletonId: int) -> dict:
        """
        Add an optional column content to the server

        :param str content: The content of the optional column
        :param id optColumnId: The mapped column id
        :param id requirementSkeletonId: The mapped requirement skeleton category
        :return dict: The requested optional column content
        """
        data = {
            'content': content,
            'optColumn': {
                'id': optColumnId,
            },
            'requirementSkeleton': {
                'id': requirementSkeletonId,
            }
        }
        return self.post('optColumnContents', data)

    def updateOptColumnContent(self, id_: int, content: str = None, optColumnId: int = None,
                               requirementSkeletonId: int = None) -> dict:
        """
        Updates an optional column content

        :param int id_: The Id of the object
        :param str content: The content of the optional column
        :param id optColumnId: The mapped column id
        :param id requirementSkeletonId: The mapped requirement skeleton category
        :return dict: The requested optional column content
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        data = self.getOptColumnContent(id_)
        if content is not None:
            data['content'] = content
        if optColumnId is not None:
            data['optColumn'] = {'id': optColumnId}
        if requirementSkeletonId is not None:
            data['requirementSkeleton'] = {'id': requirementSkeletonId}
        return self.put('optColumnContents', data)

    def deleteOptColumnContent(self, id_: int) -> bool:
        """
        Deletes an optional column content

        :param int id_: The Id of the object
        :return bool: The requested optional column content
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.delete('optColumnContents/%s' % id_)

    def getProjectType(self, id_: int) -> dict:
        """
        Gets a project type from the server

        :param int id_: The Id of the object
        :return dict: The requested project type
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.get('projectTypes/%s' % id_)

    def getProjectTypes(self) -> list:
        """
        Gets all project types

        :return list: all project types
        """
        return self.getCached('projectTypes')

    # noinspection DuplicatedCode
    def addProjectType(self, name: str, description: str, statusColumnIds: List[int] = None,
                       optColumnIds: List[int] = None, showOrder: int = 0, active: bool = False) -> dict:
        """
        Adds a project type to the server

        :param str name: The name of the object
        :param str description: The description of the object
        :param list statusColumnIds: A list of mapped status column Ids
        :param list optColumnIds: A list of mapped optional column Ids
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The requested optional column content
        """
        if optColumnIds is None:
            optColumnIds = []
        if statusColumnIds is None:
            statusColumnIds = []
        optColumnList = []
        statusColumnList = []

        for i in optColumnIds:
            optColumnList.append({'id': i})
        for i in statusColumnIds:
            statusColumnList.append({'id': i})
        data = {
            'name': name,
            'description': description,
            'showOrder': showOrder,
            'active': active,
            'statusColumns': statusColumnList,
            'optColumns': optColumnList,
        }
        return self.post('projectTypes', data)

    def updateProjectType(self, id_: int, name: str = None, description: str = None, statusColumnIds: List[int] = None,
                          optColumnIds: List[int] = None, showOrder: int = None, active: bool = None) -> dict:
        """
        Updates a specific project type

        :param int id_: The Id of the object
        :param str name: The name of the object
        :param str description: The description of the object
        :param list statusColumnIds: A list of mapped status column Ids
        :param list optColumnIds: A list of mapped optional column Ids
        :param int showOrder: The show order of the object, default is 0
        :param bool active: Sets if the object is active, default is False
        :return dict: The requested optional column content
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        data = self.getProjectType(id_)
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if showOrder is not None:
            data['showOrder'] = showOrder
        if active is not None:
            data['active'] = active
        if optColumnIds is not None:
            optColumnList = []
            for i in optColumnIds:
                optColumnList.append({'id': i})
            data['optColumns'] = optColumnList
        if statusColumnIds is not None:
            statusColumnList = []
            for i in statusColumnIds:
                statusColumnList.append({'id': i})
            data['statusColumns'] = statusColumnList
        return self.put('projectTypes', data)

    def deleteProjectType(self, id_: int) -> bool:
        """
        Deletes a project type

        :param int id_: The Id of the object
        :return bool: The requested project type
        """
        if id_ is None:
            raise ValueError('Id can\'t be none')
        return self.delete('projectTypes/%s' % id_)
    
    def getStatusColumn(self, id_) -> dict:
        """
        Returns a specific status column instance

        :param int id_: The Id of the object The Id of the object
        :return dict: The requested data
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none. Use getCollectionCategories for a list of all collection categories')
        return self.get('statusColumns/%s' % id_)

    def getStatusColumns(self) -> list:
        """
        Returns all status column instances

        :return dict: The requested data
        """
        return self.getCached('statusColumns')
    
    def addStatusColumn(self, name: str, description: str, isEnum: bool = False, 
                        showOrder: int = 0, active: bool = True) -> dict:
        data = {
                'name': name,
                'description': description,
                'showOrder': showOrder,
                'active': active,
                'id': None,
                'isEnum': isEnum
            }
        return self.post('statusColumns', data) 
    
    def getStatusColumnValues(self) -> list:
        """
        Returns all status column value instances

        :return dict: The requested data
        """
        return self.getCached('statusColumnValues')
    
    def addStatusColumnValue(self, name: str, description: str, statusColumnId: int,
                             showOrder: int = 0, active: bool = True) -> dict:
        data = {
                'name': name,
                'description': description,
                'statusColumn': {
                            'id': statusColumnId,
                        },
                'showOrder': showOrder,
                'active': active,
                'id': None
            }
        return self.post('statusColumnValues', data) 
    
    def getAlternativeSets(self) -> list:
        """
        Returns all alternative set instances

        :return dict: The requested data
        """
        return self.getCached('alternativeSets')
    
    
    def addAlternativeSet(self, name: str, description: str, optColumnId: id, 
                          showOrder: int = 0, active: bool = True) -> dict:
        data = {
                'name': name,
                'description': description,
                'optColumn': {
                        'id': optColumnId,
                    },
                'showOrder': showOrder,
                'active': active,
                'id': None
            }
        return self.post('alternativeSets', data) 
    
    def getAlternativeInstance(self, id_) -> dict:
        """
        Returns a specific alternative instance

        :param int id_: The Id of the object The Id of the object
        :return dict: The requested data
        :raises ValueError: Error if the Id is None
        """
        if id_ is None:
            raise ValueError('Id can\'t be none. Use getCollectionCategories for a list of all collection categories')
        return self.get('alternativeInstances/%s' % id_)

    def getAlternativeInstances(self) -> list:
        """
        Returns all alternative instances

        :return dict: The requested data
        """
        return self.getCached('alternativeInstances')
    
    def addAlternativeInstance(self, content: str, alternativeSetId: id, 
                               requirementSkeletonId: id) -> dict:
        data = {
                'content': content,
                'alternativeSet': {
                        'id': alternativeSetId,
                        },
                'requirementSkeleton': {
                        'id': requirementSkeletonId
                        },
                'id': None
        }
        return self.post('alternativeInstances', data) 
 
class SecurityRatEntryList(UserList):
    """
    A custom list to handle the server responses
    """

    def makeDictList(self) -> dict:
        """
        Builds a dict out of a returned list

        :return dict: Built dict
        """
        dictList = {}
        for d in self.data:
            dictList[d['id']] = dict(d)
            for k, d1 in d.items():
                if isinstance(d1, list):
                    dictList[d['id']][k] = SecurityRatEntryList(d1).makeDictList()
            del dictList[d['id']]['id']
        return dictList

    def removeDeactivated(self) -> UserList:
        """
        Removes all deactivated items from a list

        :return list: cleaned list
        """
        self.data = self.removeDeactivatedList(self.data)
        return SecurityRatEntryList(self.data)  # @ToDo: fix that

    def removeDeactivatedDict(self, data: dict) -> Union[dict, None]:
        """
        Recursive function for removal process

        :param dict data: Input data
        :return dict: output data
        """
        for k, v in data.items():
            if k == 'active' and v is False:
                return None
            elif isinstance(v, dict):
                r = self.removeDeactivatedDict(v)
                if r is None:
                    return None
                else:
                    data[k] = r
        return data

    def removeDeactivatedList(self, data: list) -> list:
        """
        Recursive function for removal process

        :param list data: Input data
        :return list: output data
        """
        for k, v in enumerate(data):
            if isinstance(v, dict):
                data[k] = self.removeDeactivatedDict(v)
        return [x for x in data if x is not None]
    
