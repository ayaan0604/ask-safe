import "./navbar.css"

export default function Navbar(){



    return (
        <div className="navbar">
            <div className="logo">
                <p>AskSafe
            </p></div>

            <div className="options">
                <a>Login</a>
                <a>Signup</a>
                <a onClick={()=>{window.open("https://www.github.com/ayaan0604/ask-safe", '_blank').focus()}}>GitHub</a>
            </div>
        </div>
    )
}