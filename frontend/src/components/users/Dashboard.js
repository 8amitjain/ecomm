import React, { Fragment } from "react";
import Login from "./Login";
import Register from "./Register";
import Users from "./Users";

export default function Dashboard() {
  return (
    <Fragment>
      <Login />
      <Register />
      <Users />
    </Fragment>
  );
}
