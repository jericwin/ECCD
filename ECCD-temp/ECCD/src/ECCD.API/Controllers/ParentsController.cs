using ECCD.Application.Common.Models;
using ECCD.Application.Parents.Queries;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ECCD.API.Controllers;

[Authorize]
public class ParentsController : ApiControllerBase
{
    [HttpGet]
    public async Task<ActionResult<ApiResponse<List<ParentDto>>>> GetAll()
    {
        var result = await Mediator.Send(new GetParentsQuery());
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<List<ParentDto>>.Fail("GET_PARENTS_FAILED", result.Error ?? "Failed to load parents."));
        }
        return Ok(ApiResponse<List<ParentDto>>.Success(result.Data!));
    }
}
