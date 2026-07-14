using MediatR;
using Microsoft.AspNetCore.Mvc;

namespace ECCD.API.Controllers;

/// <summary>
/// Base controller — all API controllers inherit from this.
/// Provides MediatR ISender and sets the versioned route prefix.
/// </summary>
[ApiController]
[Route("api/v1/[controller]")]
public abstract class ApiControllerBase : ControllerBase
{
    private ISender? _mediator;
    protected ISender Mediator => _mediator ??= HttpContext.RequestServices.GetRequiredService<ISender>();
}
