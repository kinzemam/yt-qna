import Header from "../components/header"

export default function Signup(props) {
    return <div>
        <Header />
        <div className="auth container my-5 px-5 py-5">
            <div className="text-center mb-4">
                <h3 className="py-0 my-0">Create account</h3>
            </div>
            <form onSubmit={props.handleSubmit}>
                <div className="mb-4">
                    <label htmlFor="email" className="form-label px-1">Your Email</label>
                    <input type="email" className="form-control" id="email" name="email" placeholder="Email Address" />
                </div>
                <div className="mb-3">
                    <label htmlFor="password" className="form-label px-1">Set Password</label>
                    <input type="password" className="form-control" id="password" name="password" placeholder="Your Password" />
                    {/* <p className="mx-1 my-2" ><u><a href="/">Forgot Password</a></u></p> */}
                </div>
                <div className="mb-1 text-center">
                    <input type="submit" className="px-3 py-2 btn btn-outline-dark my-btn" value="Sign Up" />
                </div>
            </form>
        </div>
    </div>
}