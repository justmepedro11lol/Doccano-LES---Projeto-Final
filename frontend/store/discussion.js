export const state = () => ({
  isDiscussionEnded: false
})

export const mutations = {
  setDiscussionEnded(state, isEnded) {
    state.isDiscussionEnded = isEnded
  }
}

export const getters = {
  isDiscussionEnded(state) {
    return state.isDiscussionEnded
  }
}

export const actions = {
  endDiscussion({ commit }) {
    commit('setDiscussionEnded', true)
    // Persistir isso em localStorage para manter o estado entre recarregamentos
    if (process.client) {
      localStorage.setItem('discussionEnded', 'true')
    }
  },
  
  initDiscussionState({ commit }) {
    if (process.client) {
      const isEnded = localStorage.getItem('discussionEnded') === 'true'
      commit('setDiscussionEnded', isEnded)
    }
  }
} 