import axios from 'axios'
import router from '@/router'
import { useAlertStore } from '@/stores/alertStore'
import { useSettingsStore } from '@/stores/settingsStore'

axios.interceptors.request.use((config) => {
  var settingsStore = useSettingsStore()

  config.baseURL = settingsStore.apiUrl
  if (settingsStore.token) {
    config.headers.Authorization = `Bearer ${settingsStore.token}`
  }

  return config
})

// Prefer the API's own explanation over "Request failed with status code 500",
// which tells the user nothing about what to do.
const apiErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail

  if (typeof detail === 'string') {
    return detail
  }
  if (Array.isArray(detail) && detail[0]?.msg) {
    return detail[0].msg
  }
  if (error?.response) {
    return `${fallback} (HTTP ${error.response.status})`
  }
  return `${fallback}: could not reach the server`
}

// Every API method goes through here: returns the response data, or throws an
// Error whose message is the API's own explanation when it gives one.
const call = async (failure, request) => {
  try {
    const response = await request()
    return response.data
  } catch (error) {
    throw new Error(apiErrorMessage(error, failure), { cause: error })
  }
}

// True while a 401 is already being handled, so a burst of requests that all
// fail at once (a page loading several resources in parallel) produces one
// redirect and one toast instead of one per request.
let handlingUnauthorized = false

// An expired or deleted token otherwise surfaces as a generic error toast
// per call site, with no path to recovery. On 401, sign the user out and
// send them to Settings to re-enter a token — unless they're already there,
// where a 401 means the token they're testing is bad and the page's own
// error handling should explain that instead.
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    const isUnauthorized = error?.response?.status === 401
    const onSettingsPage = router.currentRoute.value.name === 'settings'

    if (!isUnauthorized || onSettingsPage) {
      return Promise.reject(error)
    }

    if (!handlingUnauthorized) {
      handlingUnauthorized = true
      useSettingsStore().setToken('')
      useAlertStore().addAlert({
        type: 'error',
        message: apiErrorMessage(error, 'Your session has expired, please sign in again')
      })
      router.push({ name: 'settings' }).finally(() => {
        handlingUnauthorized = false
      })
    }

    // Swallow the rejection instead of letting it reach the call site: the
    // view is being redirected away, and every call site's own catch block
    // would otherwise add a second, more generic "Error fetching X" toast
    // right on top of the explanation above.
    return new Promise(() => {})
  }
)

// Processes API
const processesAPI = {
  getProcesses: (include_deleted = false) =>
    call('Error fetching processes', () =>
      axios.get(`/processes`, { params: { include_deleted } })
    ),
  createProcess: (processData) =>
    call('Error creating process', () => axios.post(`/processes`, processData)),
  getProcess: (process_id) =>
    call('Error reading process', () => axios.get(`/processes/${process_id}`)),
  updateProcess: (process_id, processData) =>
    call('Error updating process', () => axios.put(`/processes/${process_id}`, processData)),
  deleteProcess: (process_id) =>
    call('Error deleting process', () => axios.delete(`/processes/${process_id}`)),
  getTriggers: (process_id) =>
    call('Error fetching triggers', () => axios.get(`/processes/${process_id}/trigger`)),
  createTrigger: (process_id, triggerData) =>
    call('Error creating trigger', () =>
      axios.post(`/processes/${process_id}/trigger`, triggerData)
    )
}

// Workqueues API
const workqueuesAPI = {
  getWorkqueues: (include_deleted = false) =>
    call('Error fetching workqueues', () =>
      axios.get(`/workqueues`, { params: { include_deleted } })
    ),
  getWorkqueuesWithInformation: (include_deleted = false) =>
    call('Error fetching workqueues', () =>
      axios.get(`/workqueues/information`, {
        params: { include_deleted }
      })
    ),
  createWorkqueue: (workqueueData) =>
    call('Error creating workqueue', () => axios.post(`/workqueues`, workqueueData)),
  getWorkqueue: (queue_id) =>
    call('Error reading workqueue', () => axios.get(`/workqueues/${queue_id}`)),
  getWorkqueueInformation: (queue_id) =>
    call('Error reading workqueue information', () =>
      axios.get(`/workqueues/${queue_id}/information`)
    ),
  updateWorkqueue: (queue_id, workqueueData) =>
    call('Error updating workqueue', () => axios.put(`/workqueues/${queue_id}`, workqueueData)),
  deleteWorkqueue: (queue_id) =>
    call('Error deleting workqueue', () => axios.delete(`/workqueues/${queue_id}`)),
  clearWorkqueue: async (queue_id, workitem_status = null, days_older_than = null) => {
    if (workitem_status === '') workitem_status = null
    if (days_older_than === '') days_older_than = null
    return call('Error clearing workqueue', () =>
      axios.post(`/workqueues/${queue_id}/clear`, {
        workitem_status,
        days_older_than
      })
    )
  },
  addWorkitem: (queue_id, workitemData) =>
    call('Error adding workitem', () => axios.post(`/workqueues/${queue_id}/add`, workitemData)),
  getNextWorkitem: (queue_id) =>
    call('Error fetching next workitem', () => axios.get(`/workqueues/${queue_id}/next_item`)),
  getWorkItems: (workqueue_id, page = 1, size = 20, search = '') =>
    call('Error fetching sessions', () =>
      axios.get(`/workqueues/${workqueue_id}/items`, {
        params: { page: page, size: size, search: search }
      })
    )
}

// Credentials API
const credentialsAPI = {
  getCredentials: (include_deleted = false) =>
    call('Error fetching credentials', () =>
      axios.get(`/credentials`, { params: { include_deleted } })
    ),
  createCredential: (credentialData) =>
    call('Error creating credential', () => axios.post(`/credentials`, credentialData)),
  readCredential: (credential_id) =>
    call('Error reading credential', () => axios.get(`/credentials/${credential_id}`)),
  updateCredential: (credential_id, credentialData) =>
    call('Error updating credential', () =>
      axios.put(`/credentials/${credential_id}`, credentialData)
    ),
  deleteCredential: (credential_id) =>
    call('Error deleting credential', () => axios.delete(`/credentials/${credential_id}`)),
  getEncryptionStatus: () =>
    call('Error fetching encryption status', () => axios.get(`/credentials/encryption`)),
  reencryptCredentials: () =>
    call('Error encrypting credentials', () => axios.post(`/credentials/reencrypt`))
}

const resourcesAPI = {
  getResources: (include_deleted = false) =>
    call('Error fetching resources', () =>
      axios.get(`/resources`, { params: { include_deleted } })
    ),
  createResource: (resourceData) =>
    call('Error creating resource', () => axios.post(`/resources`, resourceData)),
  getResource: (resource_id) =>
    call('Error reading resource', () => axios.get(`/resources/${resource_id}`)),
  updateResource: (resource_id, resourceData) =>
    call('Error updating resource', () => axios.put(`/resources/${resource_id}`, resourceData))
}

const sessionsAPI = {
  getSessions: (include_deleted = false, page = 1, size = 20, search = '') =>
    call('Error fetching sessions', () =>
      axios.get(`/sessions`, {
        params: { page: page, size: size, search: search, include_deleted: include_deleted }
      })
    ),
  getSession: (session_id) =>
    call('Error reading session', () => axios.get(`/sessions/${session_id}`)),
  createSession: (process_id, parameters = null) =>
    call('Error creating session', () =>
      axios.post(`/sessions`, { process_id: process_id, parameters: parameters })
    ),
  updateStatus: (session_id, status) =>
    call('Error updating session status', () =>
      axios.put(`/sessions/${session_id}/status`, { status })
    ),
  getByResourceId: (resource_id) =>
    call('Error fetching sessions by resource', () =>
      axios.get(`/sessions/by_resource_id/${resource_id}`)
    ),
  getNewSessions: () => call('Error fetching new sessions', () => axios.get(`/sessions/new`)),
  getProcessActivitySummary: (hours = 24) =>
    call('Error fetching process activity summary', () =>
      axios.get(`/sessions/activity-summary`, { params: { hours } })
    )
}

const triggersAPI = {
  getTriggers: (include_deleted = false) =>
    call('Error fetching triggers', () => axios.get(`/triggers`, { params: { include_deleted } })),
  updateTrigger: (trigger_id, triggerData) =>
    call('Error updating trigger', () => axios.put(`/triggers/${trigger_id}`, triggerData)),
  deleteTrigger: (trigger_id) =>
    call('Error deleting trigger', () => axios.delete(`/triggers/${trigger_id}`)),
  getUpcomingExecutions: (hours_ahead = 24) =>
    call('Error fetching upcoming executions', () =>
      axios.get(`/triggers/upcoming`, { params: { hours_ahead } })
    )
}

const auditLogsAPI = {
  getAuditLogs: (session_id, page = 1, size = 20, search = '') =>
    call('Error fetching sessions', () =>
      axios.get(`/audit-logs/${session_id}`, {
        params: { page: page, size: size, search: search }
      })
    ),
  getByWorkItemId: (workitem_id) =>
    call('Error fetching session logs by workitem', () =>
      axios.get(`/audit-logs/by_workitem/${workitem_id}`)
    )
}

const workitemsApi = {
  getWorkItem: (workitem_id) =>
    call('Error reading workitem', () => axios.get(`/workitems/${workitem_id}`)),
  updateWorkItem: (workitem_id, workitemData) =>
    call('Error updating workitem', () => axios.put(`/workitems/${workitem_id}`, workitemData)),
  updateWorkItemStatus: (workitem_id, status) =>
    call('Error updating workitem status', () =>
      axios.put(`/workitems/${workitem_id}/status`, { status })
    )
}

const accessTokensApi = {
  getAccessTokens: () => call('Error fetching access tokens', () => axios.get(`/accesstokens`)),

  getAccessToken: (token) =>
    call('Error reading access token', () => axios.get(`/accesstokens/${token}`)),

  createAccessToken: (identifier) =>
    call('Error creating access token', () => axios.post(`/accesstokens`, { identifier })),
  deleteAccessToken: (token) =>
    call('Error deleting access token', () => axios.delete(`/accesstokens/${token}`))
}

const incidentsAPI = {
  getIncidents: (page = 1, size = 20, search = '', status = null) =>
    call('Error fetching incidents', () =>
      axios.get(`/incidents`, {
        params: { page, size, search, ...(status && { status }) }
      })
    ),
  getOpenIncidents: () => call('Error fetching open incidents', () => axios.get(`/incidents/open`)),
  getOpenIncidentCount: () =>
    call('Error fetching open incident count', () => axios.get(`/incidents/open/count`)).then(
      (data) => data.count
    ),
  dismissAllIncidents: () =>
    call('Error dismissing all incidents', () => axios.post(`/incidents/dismiss-all`)).then(
      (data) => data.dismissed
    ),
  dismissIncidents: (ids) =>
    call('Error dismissing incidents', () => axios.post(`/incidents/dismiss`, { ids })).then(
      (data) => data.dismissed
    ),
  getIncident: (id) => call('Error reading incident', () => axios.get(`/incidents/${id}`)),
  resolveIncident: (id, status, resolution_note) =>
    call('Error resolving incident', () =>
      axios.put(`/incidents/${id}/resolve`, { status, resolution_note })
    ),
  deleteIncident: (id) => call('Error deleting incident', () => axios.delete(`/incidents/${id}`))
}

// Health API
const healthAPI = {
  getHealth: () => call('Error fetching health', () => axios.get(`/health`))
}

// Export APIs for use in Vue components or elsewhere
export {
  healthAPI,
  processesAPI,
  workqueuesAPI,
  credentialsAPI,
  resourcesAPI,
  sessionsAPI,
  auditLogsAPI,
  triggersAPI,
  workitemsApi,
  accessTokensApi,
  incidentsAPI
}
