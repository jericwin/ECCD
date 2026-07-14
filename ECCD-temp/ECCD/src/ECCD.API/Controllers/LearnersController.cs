using ECCD.Application.Common.Models;
using ECCD.Application.Learners.Commands;
using ECCD.Application.Learners.Queries;
using ECCD.Domain.Enums;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ECCD.API.Controllers;

[Authorize]
public class LearnersController : ApiControllerBase
{
    [HttpPost]
    [Authorize(Roles = "Teacher,Administrator")]
    public async Task<ActionResult<ApiResponse<Guid>>> Register(RegisterLearnerCommand command)
    {
        var result = await Mediator.Send(command);
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<Guid>.Fail("REGISTER_LEARNER_FAILED", result.Error ?? "Failed to register learner."));
        }
        return Ok(ApiResponse<Guid>.Success(result.Data!));
    }

    [HttpPost("{id}/enroll")]
    [Authorize(Roles = "Teacher,Administrator")]
    public async Task<ActionResult<ApiResponse<object>>> Enroll(Guid id, EnrollLearnerCommand command)
    {
        if (id != command.LearnerId)
        {
            return BadRequest(ApiResponse<object>.Fail("BAD_REQUEST", "Parameter ID does not match body ID."));
        }

        var result = await Mediator.Send(command);
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<object>.Fail("ENROLLMENT_FAILED", result.Error ?? "Failed to enroll learner."));
        }
        return Ok(ApiResponse<object>.Success(null!));
    }

    [HttpGet]
    public async Task<ActionResult<ApiResponse<PagedResult<LearnerDto>>>> GetLearners(
        [FromQuery] string? searchQuery,
        [FromQuery] Guid? classroomId,
        [FromQuery] Gender? gender,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 10)
    {
        var query = new GetLearnersQuery
        {
            SearchQuery = searchQuery,
            ClassroomId = classroomId,
            Gender = gender,
            Page = page,
            PageSize = pageSize
        };

        var result = await Mediator.Send(query);
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<PagedResult<LearnerDto>>.Fail("GET_LEARNERS_FAILED", result.Error ?? "Failed to query learners."));
        }
        
        var meta = new ApiMeta
        {
            Page = result.Data!.Page,
            PageSize = result.Data.PageSize,
            TotalCount = result.Data.TotalCount,
            TotalPages = result.Data.TotalPages
        };
        
        return Ok(ApiResponse<PagedResult<LearnerDto>>.Success(result.Data!, meta));
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<ApiResponse<LearnerDetailDto>>> GetById(Guid id)
    {
        var result = await Mediator.Send(new GetLearnerByIdQuery(id));
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<LearnerDetailDto>.Fail("GET_LEARNER_FAILED", result.Error ?? "Failed to load learner details."));
        }
        return Ok(ApiResponse<LearnerDetailDto>.Success(result.Data!));
    }
}
