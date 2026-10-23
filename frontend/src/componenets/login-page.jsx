import TrafficLight from "./traffic-lights"
import "./login.css"
import { useState } from "react"
import { login, signup, getMe } from "../api"

export default function LoginPage({onLogin}){

    const[mode, setMode] = useState('login')
    const[loading, setLoading] = useState(false)
    const[email, setEmail] = useState("")
    const[password, setPassword] = useState("")
    const[role, setRole] = useState("employee")
    const[notice, setNotice] = useState("")
    const[error, setError] = useState("")
    

    async function handleSubmit(event){
        event.preventDefault()

        setLoading(true)

        setError('')

        try{

            if(mode === "signup"){

                const result = await signup(email, password, role)
                
                

                if(role === 'employee')
                    setNotice("Account created! You may now log in")
                else setNotice("Manager and HR roles need approval from the HR. Please check back after some time")
                
            }
            else{
                const result = await login(email, password)
                sessionStorage.setItem('access_token', result.access_token)

                const user = await getMe(result.access_token)
                onLogin(user)
    
            }

            

            
        }

            

        catch(e){
            setError(e.message)
        }

        setLoading(false)

    }

   


    return(
        <div className="login-page">
            <div className="login-header">
                <h1>{mode==='login'? "Welcome Back!" : "Create Account"}</h1>
                <div style={{width: "50px"}}>
                    <TrafficLight/>
                </div>
            </div>

            <div className="login-body">

                <div className="auth-switch">
                    <button
                        type="button"
                        onClick={()=>{
                            setMode('login')
                            setError("")
                            setNotice('')
                        }}
                    >
                        Login
                    </button>
                    
                    <button
                        type="button"
                        onClick={()=>{
                            setMode("signup")
                            setError("")
                            setNotice("")
                        }}
                    >
                        Signup
                    </button>
                    
                </div>

                <form onSubmit={handleSubmit}>
                    <label htmlFor='email'>
                        <p>Email</p>
                        <input type="email" 
                            id="email" 
                            placeholder="Enter your email"
                            value={email}
                            onChange={event=>{setEmail(event.target.value)}}
                            required
                        ></input>
                    </label>
                    <label htmlFor='password'>
                        <p>Password</p>
                        <input type="password"
                            id="password" 
                            placeholder="Enter your password"
                            value={password}
                            onChange={e=>{setPassword(e.target.value)}}
                            required
                        ></input>
                    </label>

                    {
                        mode==='signup' && (
                            <label htmlFor="role" className="role-selector"
                            ><p>Account Type</p>
                            <select id = "role"
                                value={role}
                                onChange={(e)=>{setRole(e.target.value)}}
                            >
                                <option value="employee">Employee</option>
                                <option value="manager">Manager</option>
                                <option value="hr_admin">HR</option>

                            </select>
                                
                            
                                
                            </label>

                        )

                    }

                    {error && <p className="error">{error}</p>}
                    {notice && <p className="notice">{notice}</p>}

                    <div className="login-button">
                        <button>{mode=='login'?( loading? "Logging in.." : "Login"): ( loading? "Signing up..": "Sign Up")}</button>
                    </div>
                    
                    
                </form>
            </div>

        </div>
    )
}