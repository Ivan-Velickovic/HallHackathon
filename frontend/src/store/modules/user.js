import { fetchAPI } from '@/util';

// Currently the validity of a user's token will only be checked once,
// this is to prevent a lot of requests to the backend.

const state = {
  authToken: localStorage.getItem('authToken') || '',
  isAuthenticated: false,
  isAdmin: false,
  // info: {
  //   zID: "",
  //   name: "",
  //   events: [],
  //   societies: {
  //     member: [],
  //     staff: []
  //   },
  //   permission: 0
  // },
  info: {},
    // TODO: make sure everything that will be mutated is already here.
  isLoading: true //TODO: move this into a global store
};

const getters = {
  memberSocieties(state) {
    return state.info.societies.member;
  },
  staffSocieties(state) {
    return state.info.societies.staff;
  },
  allSocieties(state) {
    return state.info.societies.member.concat(state.info.societies.staff);
  },
  isSocietyAdmin(state) {
    return state.info.societies.staff.length > 0;
  },
  allEvents() {
    return;
  }
};

const mutations = {
  authToken(state, authToken) {
    localStorage.setItem('authToken', authToken);
    state.authToken = authToken;
  },
  info(state, infoPayload) {
    // state.info.zID = info.zID,
    // state.info.name = info.name,
    // state.info.events = info.events,
    // state.info.societies.member = info.societies.member,
    // state.info.societies.staff = info.societies.staff
    // state.info.permission = info.permission
    state.info = { ...infoPayload }
  },
  resetState(state) {
    localStorage.removeItem('authToken');
    state.authToken = '';
    state.isAuthenticated = false;
    state.isAdmin = false;
    state.info = {};
  },
  setIsAdmin(state, adminState) {
    state.isAdmin = adminState;
  },
  setIsAuthenticated(state) {
    state.isAuthenticated = true;
  },
  setIsLoading(state, isLoading) {
    state.isLoading = isLoading;
  }
};

const actions = {
  async authenticateUser({ dispatch, commit }, authToken) {
    // Currently, this action should only be called if we know that the token is valid.
    commit('authToken', authToken);
    commit('setIsAuthenticated');
    await dispatch('userInfo');
    commit('setIsAdmin', getters.isSocietyAdmin);
    commit('setIsLoading', false);
  },
  async userInfo({ commit }) {
    try {
      const requests = [
        {
          url: '/api/user/info',
          method: 'POST'
        },
        {
          url: '/api/user/involvedSocs',
          method: 'GET'
        },
        {
          url: '/api/auth/permission',
          method: 'POST'
        }
      ];
      const [
        infoResponse,
        involvedSocsResponse,
        permissionResponse
      ] = await Promise.all(requests.map(r => fetchAPI(r.url, r.method)));

      // TODO: this is messy, should rather be defining in initial state or backend should not be returning undefined
      let societies;
      if (!involvedSocsResponse.data) {
        societies = {
          member: [],
          staff: []
        }
      } else {
        societies = {
          member: involvedSocsResponse.data.member,
          staff: involvedSocsResponse.data.staff
        }
      }

      const infoPayload = {
        ...infoResponse.data,
        ...permissionResponse.data,
        societies
      }
      commit('info', infoPayload);
    } catch (error) {
      console.log(error.response); //eslint-disable-line
    }
  },
  signOut({ commit }) {
    commit('resetState');
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
};
