/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-77o3o6xxp1gqs14e', // the auth0 domain prefix
    audience: 'coffee', // the audience set for the auth0 app
    clientId: 'ZP5NVyFMNrKCXz668pd42kl0gqvff5Ge', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
