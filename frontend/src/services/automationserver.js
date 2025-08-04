import axios from 'axios'
import { useSettingsStore } from '@/stores/settingsStore'

axios.interceptors.request.use((config) => {
  var settingsStore = useSettingsStore()

  config.baseURL = settingsStore.apiUrl;
  if(settingsStore.token) {
    config.headers.Authorization = `Bearer ${settingsStore.token}`
  }

  return config
})

// Processes API
const processesAPI = {
  getProcesses: async (include_deleted = false) => {
    try {
      const response = await axios.get(`/processes`, { params: { include_deleted } })
      return response.data
    } catch (error) {
      throw new Error(`Error fetching processes: ${error}`)
    }
  },
  createProcess: async (processData) => {
    try {
      const response = await axios.post(`/processes`, processData)
      return response.data
    } catch (error) {
      throw new Error(`Error creating process: ${error}`)
    }
  },
  getProcess: async (process_id) => {
    try {
      const response = await axios.get(`/processes/${process_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error reading process: ${error}`)
    }
  },
  updateProcess: async (process_id, processData) => {
    try {
      const response = await axios.put(`/processes/${process_id}`, processData)
      return response.data
    } catch (error) {
      throw new Error(`Error updating process: ${error}`)
    }
  },
  deleteProcess: async (process_id) => {
    try {
      const response = await axios.delete(`/processes/${process_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error deleting process: ${error}`)
    }
  },
  getTriggers: async (process_id) => {
    try {
      const response = await axios.get(`/processes/${process_id}/trigger`)
      return response.data
    } catch (error) {
      throw new Error(`Error fetching triggers: ${error}`)
    }
  },
  createTrigger: async (process_id, triggerData) => {
    try {
      const response = await axios.post(`/processes/${process_id}/trigger`, triggerData)
      return response.data
    } catch (error) {
      throw new Error(`Error creating trigger: ${error}`)
    }
  }
}

// Workqueues API
const workqueuesAPI = {
  getWorkqueues: async (include_deleted = false) => {
    try {
      const response = await axios.get(`/workqueues`, { params: { include_deleted } })
      return response.data
    } catch (error) {
      throw new Error(`Error fetching workqueues: ${error}`)
    }
  },
  getWorkqueuesWithInformation: async (include_deleted = false) => {
    try {
      const response = await axios.get(`/workqueues/information`, {
        params: { include_deleted }
      })
      return response.data
    } catch (error) {
      throw new Error(`Error fetching workqueues: ${error}`)
    }
  },
  createWorkqueue: async (workqueueData) => {
    try {
      const response = await axios.post(`/workqueues`, workqueueData)
      return response.data
    } catch (error) {
      throw new Error(`Error creating workqueue: ${error}`)
    }
  },
  getWorkqueue: async (queue_id) => {
    try {
      const response = await axios.get(`/workqueues/${queue_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error reading workqueue: ${error}`)
    }
  },
  updateWorkqueue: async (queue_id, workqueueData) => {
    try {
      const response = await axios.put(`/workqueues/${queue_id}`, workqueueData)
      return response.data
    } catch (error) {
      throw new Error(`Error updating workqueue: ${error}`)
    }
  },
  deleteWorkqueue: async (queue_id) => {
    try {
      const response = await axios.delete(`/workqueues/${queue_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error deleting workqueue: ${error}`)
    }
  },
  clearWorkqueue: async(queue_id, workitem_status = null, days_older_than = null) => {
    if (workitem_status === '') workitem_status = null;
    if (days_older_than === '') days_older_than = null;

    try {
      const response = await axios.post(`/workqueues/${queue_id}/clear`, {
      workitem_status,
      days_older_than
      })
      return response.data
    } catch (error) {
      throw new Error(`Error clearing workqueue: ${error}`)
    }
  },
  addWorkitem: async (queue_id, workitemData) => {
    try {
      const response = await axios.post(`/workqueues/${queue_id}/add`, workitemData)
      return response.data
    } catch (error) {
      throw new Error(`Error adding workitem: ${error}`)
    }
  },
  getNextWorkitem: async (queue_id) => {
    try {
      const response = await axios.get(`/workqueues/${queue_id}/next_item`)
      return response.data
    } catch (error) {
      throw new Error(`Error fetching next workitem: ${error}`)
    }
  },
  getWorkItems: async (workqueue_id, page = 1, size = 20, search = '') => {
    try {
      const response = await axios.get(`/workqueues/${workqueue_id}/items`, {
        params: { page: page, size: size, search: search }
      })
      return response.data
    } catch (error) {
      throw new Error(`Error fetching sessions: ${error}`)
    }
  }
}

// Credentials API
const credentialsAPI = {
  getCredentials: async (include_deleted = false) => {
    try {
      const response = await axios.get(`/credentials`, { params: { include_deleted } })
      return response.data
    } catch (error) {
      throw new Error(`Error fetching credentials: ${error}`)
    }
  },
  createCredential: async (credentialData) => {
    try {
      const response = await axios.post(`/credentials`, credentialData)
      return response.data
    } catch (error) {
      throw new Error(`${error["response"]["data"]["detail"][0]["msg"]}`)
    }
  },
  readCredential: async (credential_id) => {
    try {
      const response = await axios.get(`/credentials/${credential_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error reading credential: ${error}`)
    }
  },
  updateCredential: async (credential_id, credentialData) => {
    try {
      const response = await axios.put(`/credentials/${credential_id}`, credentialData)
      return response.data
    } catch (error) {
      throw new Error(`${error["response"]["data"]["detail"][0]["msg"]}`)
    }
  },
  deleteCredential: async (credential_id) => {
    try {
      const response = await axios.delete(`/credentials/${credential_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error deleting credential: ${error}`)
    }
  }
}

const resourcesAPI = {
  getResources: async (include_deleted = false) => {
    try {
      const response = await axios.get(`/resources`, { params: { include_deleted } })
      return response.data
    } catch (error) {
      throw new Error(`Error fetching resources: ${error}`)
    }
  },
  createResource: async (resourceData) => {
    try {
      const response = await axios.post(`/resources`, resourceData)
      return response.data
    } catch (error) {
      throw new Error(`Error creating resource: ${error}`)
    }
  },
  getResource: async (resource_id) => {
    try {
      const response = await axios.get(`/resources/${resource_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error reading resource: ${error}`)
    }
  },
  updateResource: async (resource_id, resourceData) => {
    try {
      const response = await axios.put(`/resources/${resource_id}`, resourceData)
      return response.data
    } catch (error) {
      throw new Error(`Error updating resource: ${error}`)
    }
  }
}

const sessionsAPI = {
  getSessions: async (include_deleted = false, page = 1, size = 20, search = '') => {
    try {
      const response = await axios.get(`/sessions`, {
        params: { page: page, size: size, search: search, include_deleted: include_deleted }
      })
      return response.data
    } catch (error) {
      throw new Error(`Error fetching sessions: ${error}`)
    }
  },
  getSession: async (session_id) => {
    try {
      const response = await axios.get(`/sessions/${session_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error reading session: ${error}`)
    }
  },
  createSession: async (process_id, parameters = null) => {
    try {
      const response = await axios.post(`/sessions`, { process_id: process_id, parameters: parameters })
      return response.data
    } catch (error) {
      throw new Error(`Error creating session: ${error}`)
    }
  },
  updateStatus: async (session_id, status) => {
    try {
      const response = await axios.put(`/sessions/${session_id}/status`, { status })
      return response.data
    } catch (error) {
      throw new Error(`Error updating session status: ${error}`)
    }
  },
  getByResourceId: async (resource_id) => {
    try {
      const response = await axios.get(`/sessions/by_resource_id/${resource_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error fetching sessions by resource: ${error}`)
    }
  },
  getNewSessions: async () => {
    try {
      const response = await axios.get(`/sessions/new`)
      return response.data
    } catch (error) {
      throw new Error(`Error fetching new sessions: ${error}`)
    }
  }
}

const triggersAPI = {
  getTriggers: async (include_deleted = false) => {
    try {
      const response = await axios.get(`/triggers`, { params: { include_deleted } })
      return response.data
    } catch (error) {
      throw new Error(`Error fetching triggers: ${error}`)
    }
  },
  /*  getTrigger: async (trigger_id) => {
    try {
      const response = await axios.get(`/triggers/${trigger_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error reading trigger: ${error}`)
    }
  },*/
  updateTrigger: async (trigger_id, triggerData) => {
    try {
      const response = await axios.put(`/triggers/${trigger_id}`, triggerData)
      return response.data
    } catch (error) {
      throw new Error(`Error updating trigger: ${error}`)
    }
  },
  deleteTrigger: async (trigger_id) => {
    try {
      const response = await axios.delete(`/triggers/${trigger_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error deleting trigger: ${error}`)
    }
  },
  getUpcomingExecutions: async (hours_ahead = 24) => {
    try {
      const response = await axios.get(`/triggers/upcoming`, { params: { hours_ahead } })
      return response.data
    } catch (error) {
      throw new Error(`Error fetching upcoming executions: ${error}`)
    }
  }
}

const auditLogsAPI = {
  getAuditLogs: async (session_id, page = 1, size = 20, search = '') => {
    try {
      const response = await axios.get(`/audit-logs/${session_id}`, {
        params: { page: page, size: size, search: search }
      })
      return response.data
    } catch (error) {
      throw new Error(`Error fetching sessions: ${error}`)
    }
  },
  getByWorkItemId: async (workitem_id) => {
    try {
      const response = await axios.get(`/audit-logs/by_workitem/${workitem_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error fetching session logs by workitem: ${error}`)
    }
  }
}

const workitemsApi = {
  getWorkItem: async (workitem_id) => {
    try {
      const response = await axios.get(`/workitems/${workitem_id}`)
      return response.data
    } catch (error) {
      throw new Error(`Error reading workitem: ${error}`)
    }
  },
  updateWorkItem: async (workitem_id, workitemData) => {
    try {
      const response = await axios.put(`/workitems/${workitem_id}`, workitemData)
      return response.data
    } catch (error) {
      throw new Error(`Error updating workitem: ${error}`)
    }
  },
  updateWorkItemStatus: async (workitem_id, status) => {
    try {
      const response = await axios.put(`/workitems/${workitem_id}/status`, { status })
      return response.data
    } catch (error) {
      throw new Error(`Error updating workitem status: ${error}`)
    }
  }
}

const accessTokensApi = {
  getAccessTokens: async () => {
    try {
      const response = await axios.get(`/accesstokens`)
      return response.data
    } catch (error) {
      throw new Error(`Error fetching access tokens: ${error}`)
    }
  },

  getAccessToken: async (token) => {
    try {
      const response = await axios.get(`/accesstokens/${token}`)
      return response.data
    } catch (error) {
      throw new Error(`Error reading access token: ${error}`)
    }
  },

  createAccessToken: async (identifier) => {
    try {
      const response = await axios.post(`/accesstokens`, { identifier })
      return response.data
    } catch (error) {
      throw new Error(`Error creating access token: ${error}`)
    }
  },
  deleteAccessToken: async (token) => {
    try {
      const response = await axios.delete(`/accesstokens/${token}`)
      return response.data
    } catch (error) {
      throw new Error(`Error deleting access token: ${error}`)
    }
  }
}

// Export APIs for use in Vue components or elsewhere
export {
  processesAPI,
  workqueuesAPI,
  credentialsAPI,
  resourcesAPI,
  sessionsAPI,
  auditLogsAPI,
  triggersAPI,
  workitemsApi,
  accessTokensApi
}
