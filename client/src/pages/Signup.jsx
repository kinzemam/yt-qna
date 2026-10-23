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
                {props.error && (<div className="errorBox mb-3 btn"><input className="px-2 py-2 btn " type="text" name="error" id="error" value={props.error} disabled/></div>) }
                <div className="mb-3 text-center">
                    <input type="submit" className="px-3 py-2 btn btn-outline-dark my-btn" value="Sign Up" />
                </div>
            </form>
            <div className="mb-1 text-center">
                    <a href="/login"><input type="submit" className="px-3 py-2 btn btn-dark my-btn" value="Sign In" /></a>
            </div>
        </div>
    </div>
}