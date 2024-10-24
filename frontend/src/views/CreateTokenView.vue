<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <content-card title="Create token">
          <div class="card-body">
            <token-form @save="saveToken" v-if="token === null"></token-form>

            <div v-if="token !== null">
              <p>Token has been created, please copy this token value as it will never be shown again:</p>
              <pre>{{ token.access_token }}</pre>
            </div>

          </div>
        </content-card>
      </div>

      <div class="col-sm-4"></div>
    </div>
  </div>
</template>

<script>
import { accessTokensApi } from '@/services/automationserver.js'

import { useAlertStore } from '../stores/alertStore'

import ContentCard from '@/components/ContentCard.vue'
import TokenForm from '@/components/TokenForm.vue'

const alertStore = useAlertStore()

export default {
  data() {
    return {
      token: null
    }
  },
  components: { ContentCard, TokenForm },

  methods: {
    async saveToken(identifier) {
      try {
        this.token = await accessTokensApi.createAccessToken(identifier)

        alertStore.addAlert({
          type: 'success',
          message: "'" + identifier + "' was created"
        })
      } catch (error) {
        console.log(error)
        alertStore.addAlert({ type: 'danger', message: error })
      }
    }
  }
}
</script>

<style scoped>
/* Add custom styles here */
</style>
