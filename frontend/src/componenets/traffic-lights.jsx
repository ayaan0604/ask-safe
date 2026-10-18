


export default function TrafficLight(){



    return(
        <div className="traffic-light" style={{
            
            display:"flex",
            flexDirection:"row",
            justifyContent:"space-between",
            width:"100%"
            
        }}>
            <div style={{width: "12px", backgroundColor:"#ff3131", height: '12px', borderRadius:"100%"}}></div>
            <div style={{width: "12px", backgroundColor:"#ffde59", height: '12px', borderRadius:"100%"}}></div>
            <div style={{width: "12px", backgroundColor:"#7ed957", height: '12px', borderRadius:"100%"}}></div>
          
        </div>
    )
}