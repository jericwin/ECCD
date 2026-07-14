using Microsoft.AspNetCore.Mvc;

namespace ECCD.API.Controllers;

/// <summary>
/// Health check endpoint — returns 200 OK for smoke testing.
/// </summary>
public class HealthController : ApiControllerBase
{
    [HttpGet]
    public IActionResult Get()
    {
        return Ok(new
        {
            Status = "Healthy",
            Timestamp = DateTime.UtcNow,
            Version = "1.0.0"
        });
    }
}
