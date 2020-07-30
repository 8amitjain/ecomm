import React, { Component, Fragment } from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { getUsers } from "../../actions/users";

export class Users extends Component {
  static propTypes = {
    users: PropTypes.array.isRequired,
  };

  componentDidMount() {
    this.props.getUsers();
  }
  render() {
    return (
      <Fragment>
        <h2>User List</h2>
        <table class="table table-striped">
          <thead class="thead-dark">
            <tr>
              <th scope="col">Email</th>
              <th scope="col"></th>
            </tr>
          </thead>
          <tbody>
            {this.props.users.map((user) => (
              <tr key={user}>
                <td>{user}</td>
                <td>
                  <button className="btn btn-danger btn-sm">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Fragment>
    );
  }
}
const mapStateToProps = (state) => ({
  users: state.users.users,
});
export default connect(mapStateToProps, { getUsers })(Users);
