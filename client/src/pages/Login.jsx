import Header from "../components/header"
export default function Login(props) {
    return <div>
        <Header />
        <div className="auth container my-5 px-5 py-5">
            <div className="h2 mb-4">
                Welcome Back,
            </div>
            <form onSubmit={props.handleSubmit}>
                <div className="mb-4">
                    <label htmlFor="email" className="form-label px-1">Email address</label>
                    <input type="email" className="form-control" id="email" name='email' placeholder="Enter your email" />
                </div>
                <div className="mb-1">
                    <div className="apart">
                        <label htmlFor="password" className="form-label px-1">Password</label>
                        <span className="px-1"><u><a href="/">Forgot Password</a></u></span>
                    </div>

                    <input type="password" className="form-control" id="password" name="password" placeholder="Enter your password" />
                    <p className="mx-1 my-2" ></p>
                </div>
                {!props.passwordCheck && (
                    <div className="mb-4 ">
                        <input id="incorrect" type="text" className="form-control incorrectPass py-2" value="Incorrect Password" disabled hidden={props.passwordCheck ? true : false}
                        />
                    </div>
                )}

                <div className="mb-3 text-center">
                    <input type="submit" className="px-3 py-2 btn btn-outline-dark my-btn" value="Lets Go!" />
                </div>
            </form>
                <div className="mb-1 text-center">
                    <a href="/signup"><input type="submit" className="px-3 py-2 btn btn-dark my-btn" value="Sign Up" /></a>
                </div>
            
        </div>
    </div>
}