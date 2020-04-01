import SignIn from '@/views/auth/SignIn.vue';
import SignUp from '@/views/auth/SignUp.vue';
import AccountActivation from '@/views/auth/AccountActivation.vue';
import ForgetPassword from '@/views/auth/ForgetPassword.vue';
import ResetPassword from '@/views/auth/ResetPassword.vue';
export default [
  {
    path: '/signin',
    name: 'signIn',
    component: SignIn,
    meta: {
        title: 'Sign In - Pointr'
    }
  },
  {
    path: '/signup',
    name: 'signUp',
    component: SignUp,
    meta: {
        title: 'Sign Up - Pointr'
    }
  },
  {
    path: '/activate/:activateToken?',
    name: 'activate',
    component: AccountActivation,
    props: true
  },
  {
    path: '/resetPassword/:forgotToken?',
    name: 'resetPassword',
    component: ResetPassword,
    props: true
  },
  {
    path: '/forgotPassword',
    name: 'forgetPassword',
    component: ForgetPassword,
  },
]